"""Simulator Scene Module

Contains Builder class to construct scene dictionary from simulator case
"""
# Inputs
from hysim import input_data as in_data
from hysim.scene import frame_transforms as frames

# Data handling
from hysim.data import spd_reader
from hysim.data import data_handling as dh

# Scene
from hysim.scene import spectra
from hysim.scene import simulator_environment as env
from hysim.scene import chaser_satellite as chas
from hysim.scene import target_satellite as targ


class SceneBuilder:
    """Builder class that constructs objects in scene and adds
    them to a single dictionary

    Attributes
    ----------
    user_inputs : in_data.Configs
        Object containing user input data
    orbit_data : frames.MissionInputProcessor
        Orbit data converted from user inputs
    integrator : dict
        Dictionary configuring mitsuba integrator
    sampler : dict
        Dictionary configuring sampler
    sun : dict
        Dictionary defining Sun object in scene
    earth : dict
        Dictionary defining Earth in the scene
    target : dict
        Dictionary defining Target spacecraft
    chaser : dict
        Dictionary defining chaser spacecraft and sensor
    scene_dict : dict
        Dictionary defining entire scene after construction. This is
        passed to Mitsuba for rendering.

    Methods
    -------
    build_integrator
        Builds the integrator dictionary
    build_sampler
        Builds the sampler dictionary
    build_earth
        Builds the Earth dictionary
    build_sun
        Builds the Sun dictionary
    build_target
        Builds the Target dictionary
    build_chaser
        Builds the Chaser dictionary
    build_scene_dict
        Builds the Scene dictionary
    """

    def __init__(
        self,
        user_inputs: in_data.Configs,
        orbit_data: frames.MissionInputProcessor,
    ):
        """Initializer

        Parameters
        ----------
        user_inputs : in_data.Configs
            Object containing user input datat
        orbit_data : frames.MissionInputProcessor
            Orbit data converted from user inputs
        """

        self.user_inputs = user_inputs
        self.orbit_data = orbit_data
        self.integrator = None
        self.sampler = None
        self.sun = None
        self.earth = None
        self.target = None
        self.chaser = None
        self.scene_dict = {"type": "scene"}

    def build_integrator(self):
        """Builds integrator dictionary"""
        self.integrator = {
            "integrator": self.user_inputs.case_config["integrator"]
        }

    def build_sampler(self):
        """Builds sampler dictionary"""
        self.sampler = {"sampler": self.user_inputs.case_config["sampler"]}

    def build_earth(self):
        """Builds Earth object dictionary"""
        earth_data_path = dh.EarthData.PATH.value
        self.earth = env.Earth()
        self.earth.mesh_path = dh.get_data_path(
            earth_data_path, dh.EarthData.MESH.value
        )
        self.earth.soil_spectrum_path = dh.get_data_path(
            earth_data_path, dh.EarthData.SOIL_SPECTRUM.value
        )
        self.earth.ocean_spectrum_path = dh.get_data_path(
            earth_data_path, dh.EarthData.OCEAN_SPECTRUM.value
        )
        self.earth.earth_image_path = dh.get_data_path(
            earth_data_path, dh.EarthData.SURFACE_BITMAP.value
        )
        self.earth.position = self.orbit_data.earth_position
        self.earth.build_dict()

    def build_sun(self):
        """Builds Sun object dictionary"""
        # --- Sun --- #
        sunlight_data_path = dh.get_data_path(
            dh.LightSourceData.PATH.value,
            dh.LightSourceData.SUNLIGHT_SPECTRUM.value,
        )
        irradiance_data = spd_reader.SPDReader(sunlight_data_path)

        sunlight_spectrum = spectra.IrradianceSpectrum(
            irradiance_data.wavelengths, irradiance_data.values
        )

        self.sun = env.Sun(sunlight_spectrum)
        self.sun.position_sun_in_simple_3d(
            self.orbit_data.sun_direction_vector
        )

        # Build dict from data:
        self.sun.build_dict()

    def build_chaser(self):
        """Builds Chaser spacecraft dictionary containing sensor parameters"""
        # --- Sensor --- #
        # TODO: Add option to choose between internal sensor data, user
        # data in spd file and selected bands

        # Get the spectrum file path
        spectrum_file = self.user_inputs.sensor_config["spectrum_file"]
        spectrum_path = dh.get_user_data_path(spectrum_file)
        spectrum_data = spd_reader.SPDReader(spectrum_path)

        # Build the spectral bands
        imaging_mode = self.user_inputs.sensor_config["imaging_mode"]

        if imaging_mode == "multispectral":
            film_bands = spectra.MultispectralFilmResponse(
                spectrum_data.wavelengths, spectrum_data.values
            )
        elif imaging_mode == "hyperspectral":
            film_bands = spectra.HyperspectralFilmResponse(
                spectrum_data.wavelengths, spectrum_data.values
            )
        else:
            raise ValueError("Imaging mode invalid")

        # Build film object
        film = chas.SpectralFilm(
            film_bands, **self.user_inputs.sensor_config["film"]
        )

        # Build camera object
        camera = chas.PerspectiveCamera(
            **self.user_inputs.sensor_config["camera"]
        )

        # Combine into sensor object
        sensor = chas.SpectralSensor(film, camera, self.sampler)
        sensor.build_dict()

        # --- Chaser Satellite --- #
        self.chaser = chas.Chaser(sensor)
        self.chaser.position = self.orbit_data.chaser_position
        self.chaser.attitude = self.user_inputs.mission_config["chaser"][
            "attitude"
        ]

        self.chaser.build_dict()

    def build_target(self):
        """Builds Target spacecraft dictionary describing object model"""
        self.target = targ.Target()
        for part_name in self.user_inputs.parts_config["components"]:
            part_input = self.user_inputs.parts_config["components"][part_name]

            # Create Part:
            part = targ.PartBuilder(part_name)

            # Assign part mesh:
            part.mesh_file = dh.get_user_data_path(part_input["file"])

            # Assign material:
            if "user_material" in part_input:
                material = part_input["user_material"]
                part.set_user_material(
                    self.user_inputs.additional_materials[material]
                )

            if "database_material" in part_input:
                part.set_database_material(part_input["database_material"])

            part.build_dict()

            self.target.add_part(part)

        self.target.position = self.orbit_data.target_position
        self.target.attitude = self.user_inputs.mission_config["target"][
            "attitude"
        ]

        self.target.build_dict()

    def build_scene_dict(self):
        """Builds scene dictionary by adding scene components to scene dict"""
        self.scene_dict.update(self.integrator)
        self.scene_dict.update(self.target.target_dict)
        self.scene_dict.update(self.chaser.chaser_dict)
        self.scene_dict.update(self.sun.sun_dict)
        self.scene_dict.update(self.earth.earth_dict)
