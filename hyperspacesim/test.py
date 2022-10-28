'''
Test script (will become main())
'''
from pprint import pprint

# Inputs
from hyperspacesim import input_data

# Data handling
from hyperspacesim.data import spd_reader
from hyperspacesim.data import data_paths
from hyperspacesim.hyperspacesim.sim.sensors import SpectralSensor

# Simulator
from hyperspacesim.sim import sensors
from hyperspacesim.sim import spectra


if __name__ == "__main__":

    print("\nTesting...\n\n")


    # Get User Inputs
    user_inputs = input_data.Configs()
    user_inputs.load_configs("example_case/")

    pprint(user_inputs.sensor_config)
    print("\n")

    # Film spectrum
    #spectrum_path = data_paths.get_spectrum_path("sensors", "VNIR")

    spectrum_path = user_inputs.sensor_config["spectrum_file"]

    spectrum_data = spd_reader.SPDReader(spectrum_path)

    hyperspectral_bands = spectra.FilmSensitivitySpectrum(
        spectrum_data.wavelengths,
        spectrum_data.values
    )

    # Create film
    film = sensors.SpectralFilm(hyperspectral_bands)

    # Build camera
    camera = sensors.ThinLenseCamera(**user_inputs.sensor_config["camera"])

    vnir_sensor = sensors.SpectralSensor(film, camera)

    pprint(vnir_sensor.build_dict())


    print(help(SpectralSensor))
