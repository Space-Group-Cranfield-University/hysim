'''
Simple test script
'''
from pprint import pprint
from hyperspacesim.sim import spectrum, sensors
from hyperspacesim.data import spd_reader, data_paths


if __name__ == "__main__":

    print("\nTesting...\n\n")

sensor_selection = "VNIR"
film_resolution = (1920,1080)
fov = 3.8
aperture = 0.2
focus_distance = 100.0

#### Commands ####
spectrum_path = data_paths.get_spectrum_path("sensors", "VNIR")

spectrum_data = spd_reader.SPDReader(spectrum_path)

hyperspectral_bands = spectrum.FilmSensitivitySpectrum(
    spectrum_data.wavelengths,
    spectrum_data.values
)

# Create film
film = sensors.SpectralFilm(hyperspectral_bands)

# Build camera
camera = sensors.ThinLenseCamera(
    field_of_view=3.8,
    aperture_radius=0.2,
    focus_distance=100.0
    )

vnir_sensor = sensors.SpectralSensor(film, camera)
