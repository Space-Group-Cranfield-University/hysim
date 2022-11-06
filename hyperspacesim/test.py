'''
Test script (will become main())
'''
from pprint import pprint

# Mitsuba
import mitsuba as mi

# Inputs
from hyperspacesim import input_data

# Data handling
from hyperspacesim.data import spd_reader
from hyperspacesim.data import data_paths

# Simulator
from hyperspacesim.sim import sensors
from hyperspacesim.sim import spectra
from hyperspacesim.sim import environment
from hyperspacesim.sim import chaser

#################################################################
# BUILD FUNCTIONS
#################################################################
def build_integrator_dict(configs):
    return {"integrator": configs}

def build_sampler_dict(configs):
    return {"sampler": configs}


if __name__ == "__main__":

    print("\nTesting...\n\n")

    #Initialise Mitsuba
    mi.set_variant("scalar_spectral")

    #####################################
    # Get User Inputs
    #####################################
    user_inputs = input_data.Configs()
    user_inputs.load_configs("example_case/")

    #--------------------------------------------------
    ###### RENDER SETTINGS ######

    # Create integrator dict
    integrator = build_integrator_dict(user_inputs.case_config["integrator"])

    # Create sampler
    sampler = build_sampler_dict(user_inputs.case_config["sampler"])

    #####################################
    # Construct the Scene
    #####################################
    sun_direction = [0.2, 0.8, 0.0]
    target_position = [0,0,0]
    target_attitude = [-30,0,0]
    chaser_position = [-250,0,0]
    chaser_attitude = [0,0,0]

    #--------------------------------------------------
    ###### Create Environment ######

    # --- Sun --- #
    sun_spectrum_path = data_paths.get_spectrum_path("light_sources", "Sun")
    irradiance_data = spd_reader.SPDReader(sun_spectrum_path) 

    sunlight_spectrum = spectra.IrradianceSpectrum(
        irradiance_data.wavelengths,
        irradiance_data.values
    )

    sun = environment.Sun(sunlight_spectrum)
    sun.position_sun_in_simple_3d(sun_direction)


    #----------------------------------------------------
    ###### BUILD CHASER #######

    # --- Sensor --- #
    # Get the spectrum file path
    spectrum_path = user_inputs.sensor_config["spectrum_file"]
    spectrum_data = spd_reader.SPDReader(spectrum_path)

    # Build the spectral bands
    hyperspectral_bands = spectra.FilmSensitivitySpectrum(
        spectrum_data.wavelengths,
        spectrum_data.values
    )

    # Build film object
    film = sensors.SpectralFilm(
            hyperspectral_bands, 
            **user_inputs.sensor_config["film"]
        )

    # Build camera object
    camera = sensors.ThinLenseCamera(**user_inputs.sensor_config["camera"])

    # Combine into sensor object
    sensor = sensors.SpectralSensor(film, camera)

    # --- Chaser Satellite --- #
    chaser_satellite = chaser.Chaser(sensor)
    chaser_satellite.set_simple_position(chaser_position)
    chaser_satellite.set_simple_attitude(chaser_attitude)


    #-----------------------------------------------------
    ###### BUILD TARGET #######
