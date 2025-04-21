from typing import Any

import numpy as np
import logging

from hysim.util.strenum import StrEnum

from hysim.configs.config import Config
from hysim.util.constants import ImagingMode

from hysim.frame_transforms import PositionData
from hysim.data import data_handling as dh, spd_reader as spdr

from hysim.mitsuba import (
    films,
    sensors,
    emitters,
    shapes,
    scene,
    bsdfs,
    spectra,
)


def _spectrum_from_path(
    path: str, imaging_mode: ImagingMode
) -> list[tuple[str, spectra.IrregularSpectrum]]:
    """Reads spectrum data from a .spd file and returns it as a list of IrregularSpectrum.
    Supports reading multiple columns of sensitivities from an .spd file.

    Parameters
    ----------
    path : str
        Path to spectrum file
    imaging_mode : ImagingMode
        The imaging mode (multispectral or hyperspectral)

    Returns
    -------
    list[tuple[str,IrregularSpectrum]]
        A collection of spectra data in the IrregularSpectrum class

    """
    spectrum_data = spdr.SPDReader(path)
    bands: list[tuple[str, spectra.IrregularSpectrum]] = []
    sensitivities = spectrum_data.values
    wavelengths = spectrum_data.wavelengths

    if imaging_mode == ImagingMode.MULTISPECTRAL:
        # NOTE: might need to refactored to properly handle single column case
        if np.ndim(sensitivities) == 1:
            sensitivities = np.expand_dims(sensitivities, axis=1)
        count = 0
        for band_data in sensitivities.T:
            bands.append(
                (
                    f"band_{count}",
                    spectra.IrregularSpectrum(
                        wavelengths=wavelengths, values=band_data
                    ),
                )
            )
            count += 1

    elif imaging_mode == ImagingMode.HYPERSPECTRAL:
        if sensitivities.ndim != 1:
            raise TypeError("Too many columns for hyperspectral data")
        for i, _ in enumerate(wavelengths[1:], start=1):
            band = spectra.IrregularSpectrum(
                wavelengths=wavelengths[i - 1 : i + 1],
                values=sensitivities[i - 1 : i + 1],
            )
            # RuntimeError: [xml_v.cpp:304] The object key '400.0_410.0' contains a '.' character, which is already used as a delimiter in the object path in the scene. Please use '_' instead.
            name = f"{wavelengths[i - 1]}_{wavelengths[i]}".replace(".", ",")
            bands.append((name, band))
    else:
        raise ValueError(
            f"Invalid imaging mode, it must be either {ImagingMode.MULTISPECTRAL} or {ImagingMode.HYPERSPECTRAL}"
        )
    return bands


class SceneBuilder:
    """Builder class that constructs objects in scene and adds
    them to a mitsuba scene class.

    Attributes
    ----------
    scene : scene.Scene
        Class object defining the entire scene after construction. This is
        passed to Mitsuba for rendering.

    spectra : list[spectra.IrregularSpectrum]
        Spectra data from the film in the scene. Used for outputting hyperspectral
        data to an .exr file in the OutputHandler class.
    """

    # Mitsuba object names:
    class Names(StrEnum):
        EARTH = "earth_mesh"
        SUN = "sun_emitter"
        CHASER = "chaser_sensor"

    def __init__(self, config: Config, position_data: PositionData):
        """Initializes the SceneBuilder class

        Parameters
        ----------
        config : Config
            Object containing user input data

        position_data : PositionData
            Scene objects positional data

        """
        self._scene = scene.Scene(integrator=config.case.integrator)
        logging.debug("Building the Earth")
        self._build_earth(position_data)
        logging.debug("Building the Sun")
        self._build_sun(position_data)
        logging.debug("Building the chaser")
        self._build_chaser(config, position_data)
        logging.debug("Building the target")
        self._build_target(config, position_data)


    def _build_earth(self, position_data: PositionData):
        earth = shapes.PlyMesh(
            to_world=position_data.earth_transform,
            filename=dh.get_earth_mesh_path(),
            material=bsdfs.DiffuseMaterial(
                reflectance=spectra.SpdSpectrum(filename=dh.get_ocean_spectrum_path())
            ),
        )
        self._scene.add_shape(SceneBuilder.Names.EARTH.value, earth)

    def _build_sun(self, position_data: PositionData):
        sun = emitters.DirectionalEmitter(
            direction=position_data.sun_direction_vector,
            irradiance=spectra.SpdSpectrum(filename=dh.get_sun_spectrum_path()),
        )

        self._scene.add_emitter(SceneBuilder.Names.SUN.value, sun)

    def _build_chaser(self, config: Config, position_data: PositionData):
        # TODO: Add option to choose between internal sensor data, user
        self._spectra = _spectrum_from_path(
            config.sensor_spectrum_path, config.sensor.imaging_mode
        )
        film = films.SpectralFilm(
            width=config.sensor.film.width,
            height=config.sensor.film.height,
        )
        film.set_spectrum(self.spectra)

        chaser = sensors.PerspectiveCamera(
            sampler=config.case.sampler,
            film=film,
            fov=config.sensor.camera.field_of_view,
            to_world=position_data.chaser_transform,
        )
        self._scene.add_sensor(SceneBuilder.Names.CHASER.value, chaser)

    def _build_target(self, config: Config, position_data: PositionData):
        for part_name, part_description in config.parts.items():
            if part_description.user_material:
                mesh_material = config.user_materials[part_description.user_material]
            elif part_description.database_material:
                mesh_material = dh.get_database_material(
                    part_description.database_material
                )
            else:
                raise ValueError("No material defined for part")
            mesh = shapes.PlyMesh(
                to_world=position_data.target_transform,
                filename=part_description.file,
                material=mesh_material,
            )

            self._scene.add_shape(part_name, mesh)

    def update_positions(self, config: Config, position_data: PositionData) -> dict[str, Any]:
        d = self._scene.asdict()
        d[SceneBuilder.Names.SUN]["direction"] = position_data.sun_direction_vector
        d[SceneBuilder.Names.EARTH]["to_world"] = position_data.earth_transform
        d[SceneBuilder.Names.CHASER]["to_world"] = position_data.chaser_transform
        for part_name in config.parts.keys():
            d[part_name]["to_world"] = position_data.target_transform
        return d

    @property
    def scene(self) -> scene.Scene:
        return self._scene

    @property
    def spectra(self) -> list[tuple[str, spectra.IrregularSpectrum]]:
        return self._spectra
