'''
Simple test script
'''
import json
import pretty_errors
from hyperspacesim.data import data_paths

if __name__ == "__main__":

    print("\nTesting...\n\n")

    #spectrum_file = "hyperspacesim\\data\\spectra\\film_vnir.spd"

    # sensor = s.ThinLenseCamera(
    #     sensor_name="A Sensor",
    #     spectral_response_file=spectrum_file,
    #     number_of_bands=51,
    #     field_of_view=3.69,
    #     aperture_radius=0.2
    # )


    print(data_paths.get_spectrum_path("sensors", "VNIR"))

    #with open("hyperspacesim/data/data_list.json", 'r', encoding="utf-8") as j:
    #    contents = json.loads(j.read())

    #print(contents["sensors"])
