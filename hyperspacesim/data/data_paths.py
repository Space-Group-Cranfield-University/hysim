'''
Functions to handle data aquisition in the package.

Adding data to the package can be done by making additions to the data_list.json.
'''
import json
from importlib import resources

def get_spectrum_path(catagory, data_name):
    '''
    Get local path to spectrum file.
    '''

    # Get path for data list
    #data_list_path = resources.path("hyperspacesim.data", "data_list.json")

    # Open data list
    with resources.path("hyperspacesim.data", "data_list.json") as data_list_path:
        #print(str(data_list_path)+" \n")
        with open(data_list_path, 'r', encoding="utf-8") as j:
            data_list = json.loads(j.read())

    # Get location of requested data
    package_path = data_list[catagory][data_name]["path"]
    file_name = data_list[catagory][data_name]["spectrum_file"]

    with resources.path(package_path, file_name) as spectrum_path:
    #    return spectrum_path
        return spectrum_path


def list_defined_materials():
    pass


def list_defined_sensors():
    pass


def list_defined_light_sources():
    pass
