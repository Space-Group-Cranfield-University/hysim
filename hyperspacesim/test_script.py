'''
Simple test script
'''
#from pprint import pprint
#import importlib.resources as rs
import hyperspacesim.data as data
import hyperspacesim.sim.sensors as s

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

    data_file = data.materials

    