from typing import Any

import logging

from hysim.util.mitsuba_types import Transform, Vector

from hysim.configs.config import Config
from hysim.util.constants import SceneEntity

from hysim.simulator import frame_transforms as ft
from hysim.data import data_handling as dh

from hysim.mitsuba import (
    films,
    sensors,
    emitters,
    shapes,
    scene,
    bsdfs,
    spectra,
    textures,
)

class SceneBuilder:
    """
    Builder class that constructs objects in scene and adds
    them to a mitsuba scene class.
    """

    def __init__(self, config: Config):
        """Initializes the SceneBuilder class

        Parameters
        ----------
        config : Config
            Object containing user input data
        """
        self._config = config
        self._scene = scene.Scene(integrator=config.case.integrator)

    def build(self):
        logging.debug("Building the Earth")
        self._build_earth()
        logging.debug("Building the Sun")
        self._build_sun()
        logging.debug("Building the chaser")
        self._build_chaser()
        logging.debug("Building the target")
        self._build_target()

    def _build_earth(self):
        earth = shapes.Sphere(
            radius=ft.earth_radius(),
            to_world=Transform(),
            material=bsdfs.DiffuseMaterial(
                reflectance=textures.BitmapTexture(
                    filename=dh.EarthData.MAP_LOW_RES,
                    wrap_mode="clamp"
                )
            )
            # material=bsdfs.BlendedMaterial(
            #     weight=textures.BitmapTexture(
            #         filename=dh.EarthData.SURFACE_BITMAP, wrap_mode="clamp"
            #     ),
            #     bsdf_0=bsdfs.DiffuseMaterial(
            #         reflectance=spectra.SpdSpectrum(filename=dh.EarthData.SOIL_SPECTRUM)
            #     ),
            #     bsdf_1=bsdfs.DiffuseMaterial(
            #         reflectance=spectra.SpdSpectrum(
            #             filename=dh.EarthData.OCEAN_SPECTRUM
            #         )
            #     ),
            # ),
        )
        self._scene.add_shape(SceneEntity.EARTH.value, earth)

    def _build_sun(self):
        sun = emitters.DirectionalEmitter(
            direction=Vector(),
            irradiance=spectra.SpdSpectrum(filename=dh.sun_spectrum_path()),
        )

        self._scene.add_emitter(SceneEntity.SUN.value, sun)

    def _build_chaser(self):
        # TODO: Add option to choose between internal sensor data, user

        film = films.SpectralFilm(
            width=self._config.sensor.film.width,
            height=self._config.sensor.film.height,
        )
        film.set_spectrum(self._config.sensor_bands)

        chaser = sensors.PerspectiveCamera(
            sampler=self._config.case.sampler,
            film=film,
            fov=self._config.sensor.camera.field_of_view,
            to_world=Transform(),
        )
        self._scene.add_sensor(SceneEntity.CHASER.value, chaser)

    def _build_target(self):
        for part_name, part_description in self._config.parts.items():
            if part_description.user_material:
                mesh_material = self._config.user_materials[part_description.user_material]
            elif part_description.database_material:
                mesh_material = dh.database_material(part_description.database_material)
            else:
                raise ValueError("No material defined for part")
            mesh = shapes.PlyMesh(
                to_world=Transform(),
                filename=part_description.file,
                material=mesh_material,
            )

            self._scene.add_shape(part_name, mesh)

    def set_positions(self, position_data: ft.PositionData) -> dict[str, Any]:
        d = self._scene.asdict()
        d[SceneEntity.SUN]["direction"] = position_data.get(SceneEntity.SUN)
        d[SceneEntity.EARTH]["to_world"] = position_data.get(SceneEntity.EARTH)
        d[SceneEntity.CHASER]["to_world"] = position_data.get(SceneEntity.CHASER)
        for part_name in self._config.parts.keys():
            d[part_name]["to_world"] = position_data.get(SceneEntity.TARGET)
        return d

    @property
    def scene(self) -> scene.Scene:
        """
        Returns
        -------
        scene : scene.Scene
            Class object defining the entire scene after construction. This is
            passed to Mitsuba for rendering.
        """
        return self._scene
