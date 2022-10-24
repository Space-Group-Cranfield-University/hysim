'''
Simple test script
'''
from pprint import pprint
from hyperspacesim.sim import spectrum, sensors
from hyperspacesim.data import spd_reader, data_paths


if __name__ == "__main__":

    print("\nTesting...\n\n")

spectrum_path = data_paths.get_spectrum_path("sensors", "VNIR")
print("Spectrum Path:\n")
print(spectrum_path)


spectrum_data = spd_reader.SPDReader(spectrum_path)
print("\n\nSpectrum Object:\n")
#print(spectrum_data.wavelengths)
#pprint(spectrum_data.values)

hyperspectral_bands = spectrum.FilmSensitivitySpectrum(
    spectrum_data.wavelengths,
    spectrum_data.values
)
print("\n\Spectrum Dict:\n")
#pprint(hyperspectral_film.build_dict())

film = sensors.SpectralFilm(hyperspectral_bands)
print("\n\Film Dict:\n")
#pprint(film)

camera = sensors.ThinLenseCamera(
    field_of_view=3.8,
    aperture_radius=0.2,
    focus_distance=100.0
    )
#print(camera)

vnir_sensor = sensors.SpectralSensor(film, camera)
#pprint(vnir_sensor)
pprint(len(hyperspectral_bands))
