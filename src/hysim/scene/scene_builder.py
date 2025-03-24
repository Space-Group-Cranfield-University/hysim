from hysim.configs.config import Config

from hysim.scene.frame_transforms import ScenePositionData
from hysim.data import data_handling as dh

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


class SceneBuilder:
    def __init__(self, config: Config, position_data: ScenePositionData):
        self._scene = scene.Scene()

        self._build_integrator(config)
        self._build_earth(position_data)
        self._build_sun(position_data)
        self._build_chaser(config, position_data)
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
        sampler = samplers.StratifiedSampler()
        sampler.sample_count = config.case.sampler.sample_count

        film = films.SpectralFilm()
        film.height = config.sensor.film.height
        film.width = config.sensor.film.width
        film.spectra = dh.spectrum_from_path(
            config.sensor_spectrum_path, config.sensor.imaging_mode
        )

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