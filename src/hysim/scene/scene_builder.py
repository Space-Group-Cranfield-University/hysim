import numpy as np
import logging

from hysim.configs.config import Config
from hysim.configs.constants import ImagingMode

from hysim.scene.frame_transforms import ScenePositionData
from hysim.data import data_handling as dh, spd_reader as spdr

from hysim.mitsuba import (
    films,
    samplers,
    sensors,
    emitters,
    shapes,
    integrators,
    scene,
    bsdfs,
    spectra,
)


def _spectrum_from_path(
    path: str, imaging_mode: ImagingMode
) -> list[spectra.IrregularSpectrum]:
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
    list[IrregularSpectrum]
        A collection of spectra data in the IrregularSpectrum class

    """
    spectrum_data = spdr.SPDReader(path)
    bands = []
    sensitivities = spectrum_data.values
    wavelengths = spectrum_data.wavelengths

    if imaging_mode == ImagingMode.MULTISPECTRAL:
        # NOTE: might need to refactored to properly handle single column case
        if np.ndim(sensitivities) == 1:
            sensitivities = np.expand_dims(sensitivities, axis=1)
        bands = [
            spectra.IrregularSpectrum(wavelengths, band_data)
            for band_data in sensitivities.T
        ]

    elif imaging_mode == ImagingMode.HYPERSPECTRAL:
        if sensitivities.ndim != 1:
            raise TypeError("Too many columns for hyperspectral data")
        for i, _ in enumerate(wavelengths[1:], start=1):
            band = spectra.IrregularSpectrum(
                wavelengths[i - 1 : i + 1], sensitivities[i - 1 : i + 1]
            )
            # RuntimeError: [xml_v.cpp:304] The object key '400.0_410.0' contains a '.' character, which is already used as a delimiter in the object path in the scene. Please use '_' instead.
            band.name = f"{wavelengths[i - 1]}_{wavelengths[i]}".replace(".", ",")
            bands.append(band)
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

    def __init__(self, config: Config, position_data: ScenePositionData):
        """Initializes the SceneBuilder class

        Parameters
        ----------
        config : Config
            Object containing user input data

        position_data : ScenePositionData
            Scene objects positional data

        """
        self._scene = scene.Scene()

        logging.debug("Building integrator")
        self._build_integrator(config)
        logging.debug("Building Earth")
        self._build_earth(position_data)
        logging.debug("Building Sun")
        self._build_sun(position_data)
        logging.debug("Building Chaser")
        self._build_chaser(config, position_data)
        logging.debug("Building Target")
        self._build_target(config, position_data)

    def _build_integrator(self, config: Config):
        integrator = integrators.PathTracer()
        integrator.max_depth = config.case.integrator.max_depth
        self._scene.set_integrator(integrator)

    def _build_earth(self, position_data: ScenePositionData):
        earth = shapes.PlyMesh()
        earth.name = "earth_mesh"
        earth.filename = dh.get_earth_mesh_path()
        earth.to_world = position_data.earth_transform
        earth.material = bsdfs.DiffuseMaterial(
            spectra.SpdSpectrum(dh.get_ocean_spectrum_path())
        )
        self._scene.add_shape(earth)

    def _build_sun(self, position_data: ScenePositionData):
        sun = emitters.DirectionalEmitter()
        sun.name = "sun_emitter"
        sun.direction = position_data.sun_direction_vector
        sun.irradiance = spectra.SpdSpectrum(dh.get_sun_spectrum_path())
        self._scene.add_emitter(sun)

    def _build_chaser(self, config: Config, position_data: ScenePositionData):

        # TODO: Add option to choose between internal sensor data, user
        sampler = samplers.StratifiedSampler()
        sampler.sample_count = config.case.sampler.sample_count

        film = films.SpectralFilm()
        film.height = config.sensor.film.height
        film.width = config.sensor.film.width
        self._spectra = _spectrum_from_path(
            config.sensor_spectrum_path, config.sensor.imaging_mode
        )
        film.spectra = self.spectra

        chaser = sensors.PerspectiveCamera()
        chaser.name = "chaser_sensor"
        chaser.sampler = sampler
        chaser.film = film
        chaser.fov = config.sensor.camera.field_of_view
        chaser.to_world = position_data.chaser_transform
        self._scene.add_sensor(chaser)

    def _build_target(self, config: Config, position_data: ScenePositionData):
        for part_name, part_description in config.parts.items():
            mesh = shapes.PlyMesh()
            mesh.name = part_name
            mesh.filename = part_description.file
            if part_description.user_material:
                mesh.material = config.user_materials[part_description.user_material]
            elif part_description.database_material:
                mesh.material = dh.get_database_material(
                    part_description.database_material
                )
            mesh.material.name = part_name + "_material"
            mesh.to_world = position_data.target_transform
            self._scene.add_shape(mesh)

    @property
    def scene(self):
        return self._scene

    @property
    def spectra(self):
        return self._spectra
