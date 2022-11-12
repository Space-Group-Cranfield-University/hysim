"""
Functions to handle data aquisition in the package.

Adding data to the package can be done by making additions to the 
data_list.json.
"""
import json
from importlib import resources

# ===== DATABASE ===== #

# --- Materials --- #
MATERIAL_PATH = "hyperspacesim.data.materials"
MATERIAL_DATA = "materials.json"

# --- Sensors --- #
SENSOR_PATH = "hyperspacesim.data.sensors"
SENSOR_DATA = "sensors.json"

# --- Light Sources --- #
LIGHTSOURCES_PATH = "hyperspacesim.data.light_sources"


def read_json_package_data(path, file):
    with resources.path(path, file) as path_data:
        with open(path_data, "r", encoding="utf-8") as j:
            return json.loads(j.read())


def get_material_from_database(material_name):
    all_materials_data = read_json_package_data(MATERIAL_PATH, MATERIAL_DATA)
    material_dict = all_materials_data[material_name]

    if material_dict["type"] == "diffuse":
        filename = material_dict["reflectance"]["filename"]
        with resources.path(MATERIAL_PATH, filename) as file_path:
            material_dict["reflectance"]["filename"] = str(file_path)

    return material_dict


def list_defined_materials():
    pass


def list_defined_sensors():
    pass


def list_defined_light_sources():
    pass
