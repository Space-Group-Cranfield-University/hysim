"""Scene"""

# Data handling
from hyperspacesim.data import spd_reader
from hyperspacesim.data import data_handling

# Scene
from hyperspacesim.scene import spectra
from hyperspacesim.scene import simulator_environment as env
from hyperspacesim.scene import chaser_satellite as chas
from hyperspacesim.scene import target_satellite as targ


class SceneBuilder:
    def __init__(self, user_inputs) -> None:
        self.user_inputs = user_inputs
        self.integrator = None
        self.sampler = None
        self.sun = None
        self.target = None
        self.chaser = None
        self.scene_dict = {"type": "scene"}

    def build_integrator(self):
        self.integrator = {
            "integrator": self.user_inputs.case_config["integrator"]
        }

    def build_sampler(self):
        self.sampler = {"sampler": self.user_inputs.case_config["sampler"]}

    def build_sun(self):
        sun_direction = [0.2, 0.8, 0.0]  # TODO: User chosen position

        # --- Sun --- #
        irradiance_data = spd_reader.SPDReader(
            data_handling.get_wehrli85_path()
        )

        sunlight_spectrum = spectra.IrradianceSpectrum(
            irradiance_data.wavelengths, irradiance_data.values
        )

        self.sun = env.Sun(sunlight_spectrum)
        self.sun.position_sun_in_simple_3d(sun_direction)

        # Build dict from data:
        self.sun.build_dict()

    def build_chaser(self):
        # --- Sensor --- #
        # Get the spectrum file path
        spectrum_path = self.user_inputs.sensor_config["spectrum_file"]
        spectrum_data = spd_reader.SPDReader(spectrum_path)

        # Build the spectral bands
        hyperspectral_bands = spectra.FilmSensitivitySpectrum(
            spectrum_data.wavelengths, spectrum_data.values
        )

        # Build film object
        film = chas.SpectralFilm(
            hyperspectral_bands, **self.user_inputs.sensor_config["film"]
        )

        # Build camera object
        camera = chas.ThinLenseCamera(
            **self.user_inputs.sensor_config["camera"]
        )

        # Combine into sensor object
        sensor = chas.SpectralSensor(film, camera, self.sampler)
        sensor.build_dict()

        # --- Chaser Satellite --- #
        self.chaser = chas.Chaser(sensor)
        self.chaser.set_simple_position(
            self.user_inputs.mission_config["chaser"]["position"]
        )
        self.chaser.set_simple_attitude(
            self.user_inputs.mission_config["chaser"]["position"]
        )

        self.chaser.build_dict()

    def build_target(self):
        """Assembles target parts and assigns materials to each part according
        to configs"""
        self.target = targ.Target()
        for part_name in self.user_inputs.parts_config["components"]:
            part_input = self.user_inputs.parts_config["components"][part_name]

            # Create Part:
            part = targ.PartBuilder(part_name)

            # Assign part mesh:
            part.mesh_file = part_input["file"]

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

        self.target.attitude = self.user_inputs.mission_config["target"][
            "attitude"
        ]
        self.target.position = self.user_inputs.mission_config["target"][
            "position"
        ]

        self.target.build_dict()

    def build_scene_dict(self):
        self.scene_dict.update(self.integrator)
        self.scene_dict.update(self.target.target_dict)
        self.scene_dict.update(self.chaser.chaser_dict)
        self.scene_dict.update(self.sun.sun_dict)
