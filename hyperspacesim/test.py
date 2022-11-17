"""
Main client script to run code. Called by user.
"""
# Packages
import mitsuba as mi

# I/O
from hyperspacesim import input_data

# Data handling
from hyperspacesim.data import spd_reader
from hyperspacesim.data import data_handling

# Simulator
from hyperspacesim import renderer
from hyperspacesim.sim import sensors
from hyperspacesim.sim import spectra
from hyperspacesim.sim import environment
from hyperspacesim.sim import chaser
from hyperspacesim.sim import target as trgt


#################################################################
# SCENE BUILDING
#################################################################
class SceneBuilder:
    def __init__(self) -> None:
        self.user_inputs = None
        self.integrator = None
        self.sampler = None
        self.sun = None
        self.target = None
        self.chaser = None
        self.scene_dict = {"type": "scene"}

    def build_integrator(self, integrator_config):
        self.integrator = {"integrator": integrator_config}

    def build_sampler(self, sampler_config):
        self.sampler = {"sampler": sampler_config}

    def build_environment(self, environment_config):
        sun_direction = [0.2, 0.8, 0.0] # TODO: User chosen position

        # --- Sun --- #
        irradiance_data = spd_reader.SPDReader(
            data_handling.get_wehrli85_path()
        )

        sunlight_spectrum = spectra.IrradianceSpectrum(
            irradiance_data.wavelengths, irradiance_data.values
        )

        self.sun = environment.Sun(sunlight_spectrum)
        self.sun.position_sun_in_simple_3d(sun_direction)

        # Build dict from data:
        self.sun.build_dict()

    def build_chaser(self, chaser_config):
        # --- Sensor --- #
        # Get the spectrum file path
        spectrum_path = self.user_inputs.sensor_config["spectrum_file"]
        spectrum_data = spd_reader.SPDReader(spectrum_path)

        # Build the spectral bands
        hyperspectral_bands = spectra.FilmSensitivitySpectrum(
            spectrum_data.wavelengths, spectrum_data.values
        )

        # Build film object
        film = sensors.SpectralFilm(
            hyperspectral_bands, **self.user_inputs.sensor_config["film"]
        )

        # Build camera object
        camera = sensors.ThinLenseCamera(**self.user_inputs.sensor_config["camera"])

        # Combine into sensor object
        sensor = sensors.SpectralSensor(film, camera, sampler)
        sensor.build_dict()

        # --- Chaser Satellite --- #
        chaser_satellite = chaser.Chaser(sensor)
        chaser_satellite.set_simple_position(
            self.user_inputs.mission_config["chaser"]["position"]
        )
        chaser_satellite.set_simple_attitude(
            self.user_inputs.mission_config["chaser"]["position"]
        )

        chaser_satellite.build_dict()
        

    def build_target():


    def build_scene_dict():


if __name__ == "__main__":

    print("\nTesting...\n\n")

    # Initialise Mitsuba
    mi.set_variant("scalar_spectral") # TODO: Set this in case config

    #####################################
    # Get User Inputs
    #####################################
    user_inputs = input_data.Configs()
    user_inputs.load_configs("example_case/") # TODO: Set this in case config?

    # pprint(user_inputs.__dict__)
    # ---------- RENDER SETTINGS ----------

    # Create integrator dict
    integrator = build_integrator_dict(user_inputs.case_config["integrator"])

    # Create sampler
    sampler = build_sampler_dict(user_inputs.case_config["sampler"])

    #####################################
    # Construct the Scene
    #####################################

    # ---------- Create Environment ----------

    # --- Sun --- #
    irradiance_data = spd_reader.SPDReader(data_handling.get_wehrli85_path())

    sunlight_spectrum = spectra.IrradianceSpectrum(
        irradiance_data.wavelengths, irradiance_data.values
    )

    sun = environment.Sun(sunlight_spectrum)
    sun.position_sun_in_simple_3d(sun_direction)

    # Build dict from data:
    sun.build_dict()

    # ---------- BUILD CHASER ----------

    # --- Sensor --- #
    # Get the spectrum file path
    spectrum_path = user_inputs.sensor_config["spectrum_file"]
    spectrum_data = spd_reader.SPDReader(spectrum_path)

    # Build the spectral bands
    hyperspectral_bands = spectra.FilmSensitivitySpectrum(
        spectrum_data.wavelengths, spectrum_data.values
    )

    # Build film object
    film = sensors.SpectralFilm(
        hyperspectral_bands, **user_inputs.sensor_config["film"]
    )

    # Build camera object
    camera = sensors.ThinLenseCamera(**user_inputs.sensor_config["camera"])

    # Combine into sensor object
    sensor = sensors.SpectralSensor(film, camera, sampler)
    sensor.build_dict()

    # --- Chaser Satellite --- #
    chaser_satellite = chaser.Chaser(sensor)
    chaser_satellite.set_simple_position(
        user_inputs.mission_config["chaser"]["position"]
    )
    chaser_satellite.set_simple_attitude(
        user_inputs.mission_config["chaser"]["position"]
    )

    chaser_satellite.build_dict()

    # ---------- BUILD TARGET ---------- #
    target = trgt.Target()
    for part_name in user_inputs.parts_config["components"]:
        part_input = user_inputs.parts_config["components"][part_name]

        # Create Part:
        part = trgt.PartBuilder(part_name)

        # Assign part mesh:
        part.mesh_file = part_input["file"]

        # Assign material:
        if "user_material" in part_input:
            material = part_input["user_material"]
            part.set_user_material(user_inputs.additional_materials[material])

        if "database_material" in part_input:
            part.set_database_material(part_input["database_material"])

        part.build_dict()

        target.add_part(part)
        # pprint(target.build_dict())

    target.attitude = user_inputs.mission_config["target"]["attitude"]
    target.position = user_inputs.mission_config["target"]["position"]

    target.build_dict()

    # ---------- ASSEMBLE SCENE ---------- #
    scene_dict = {"type": "scene"}

    lookat_settings = mi.ScalarTransform4f.look_at(
            origin=[-250, -100, 0.0],
            target=[0, 0, 0],
            up=[0, 0, -1])

    chaser_satellite.chaser_dict["sensor"]["to_world"] = lookat_settings

    scene_dict.update(integrator)
    scene_dict.update(target.target_dict)
    scene_dict.update(chaser_satellite.chaser_dict)
    scene_dict.update(sun.sun_dict)

    # print(scene_dict)

    #####################################
    # Load to mitsuba and run
    #####################################

    sim = renderer.RendererControl()
    sim.load_scene(scene_dict)
    sim.run()

    #####################################
    # Export to OpenEXR format
    #####################################

    output = renderer.OutputFormatter(sim.render)

    case_directory = "example_case/"
    output.export_as_exr(film, case_directory)
