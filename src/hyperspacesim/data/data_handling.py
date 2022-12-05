"""
Functions to handle data aquisition in the package.

Adding data to the package can be done by making additions to the 
data_list.json.
"""
import os
from importlib import resources
from enum import Enum
from pathlib import Path

import json


# ===== IO Error Handling ===== #


class DataFileNotFoundError(Exception):
    pass


class ConfigFileMissing(Exception):
    pass


# ===== DATABASE ===== #


class Kernels(Enum):
    PATH = "hyperspacesim.data.kernels"
    KERNEL_LIST = ["de440s.bsp", "geophysical.ker", "naif0012.tls"]


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


def get_user_data_path(filename):
    for root, _, files in os.walk(Path.cwd()):
        for file in files:
            if file == filename:
                return os.path.join(root, file).replace("\\", "/")

    # raise DataFileNotFoundError(
    #     f"{filename} cannot be found in the case directory"
    # )


def get_kernel_paths():
    return [
        get_data_path(Kernels.PATH.value, kernel)
        for kernel in Kernels.KERNEL_LIST.value
    ]


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
    return get_data_path(
        LightSourceData.PATH.value, LightSourceData.SUNLIGHT_SPECTRUM.value
    )


def list_defined_materials():
    raise NotImplementedError()


def list_defined_sensors():
    raise NotImplementedError()


def list_defined_light_sources():
    raise NotImplementedError()
