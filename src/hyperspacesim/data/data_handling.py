"""
Functions to handle data aquisition in the package.

Adding data to the package can be done by making additions to the 
data_list.json.
"""
import json
from importlib import resources
from enum import Enum

# ===== DATABASE ===== #


class Kernels(Enum):
    PATH = "hyperspacesim.data.kernels"
    META_KERNEL = "meta_kernel.tm"


class MaterialsData(Enum):
    PATH = "hyperspacesim.data.materials"
    MATERIALS_FILE = "materials.json"


class SensorsData(Enum):
    PATH = "hyperspacesim.data.sensors"
    SENSORS_FILE = "sensors.json"


class LightSourceData(Enum):
    PATH = "hyperspacesim.data.light_sources"
    SUNLIGHT_SPECTRUM = "wehrli85.spd"


class EarthData(Enum):
    PATH = "hyperspacesim.data.earth_model"
    SOIL_SPECTRUM = "soil.spd"
    OCEAN_SPECTRUM = "ocean.spd"
    MESH = "earth.ply"
    SURFACE_BITMAP = "earth.jpg"


def read_json_package_data(path, file):
    with resources.path(path, file) as path_data:
        with open(path_data, "r", encoding="utf-8") as j:
            return json.loads(j.read())


def get_material_from_database(material_name):
    materials_data = read_json_package_data(
        MaterialsData.PATH.value, MaterialsData.MATERIALS_FILE.value
    )
    material_dict = materials_data[material_name]

    if material_dict["type"] == "diffuse":
        filename = material_dict["reflectance"]["filename"]
        file_path = get_data_path(MaterialsData.PATH.value, filename)
        material_dict["reflectance"]["filename"] = str(file_path)

    return material_dict


def get_data_path(directory, file):
    with resources.path(directory, file) as path:
        return str(path).replace("\\", "/")


def get_sunlight_spectrum():
    print(LightSourceData.PATH.value)
    return get_data_path(
        LightSourceData.PATH.value, LightSourceData.SUNLIGHT_SPECTRUM.value
    )


def list_defined_materials():
    pass


def list_defined_sensors():
    pass


def list_defined_light_sources():
    pass
