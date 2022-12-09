"""Data Handling Module

Contains Database Enums to define data paths and functions to
handle data retrieval.
"""
import os
from importlib import resources
from enum import Enum
from pathlib import Path

import json


# ===== IO Error Handling ===== #
class DataFileNotFoundError(Exception):
    """Exception for handling file not found in database"""
    pass


class ConfigFileMissing(Exception):
    """Exception to handle missing configuration file"""
    pass


# ===== DATABASE ===== #
class Kernels(Enum):
    """Enum containing path and files for SpiceyPy kernels"""
    PATH = "hyperspacesim.data.kernels"
    KERNEL_LIST = ["de440s.bsp", "geophysical.ker", "naif0012.tls"]


class MaterialsData(Enum):
    """Enum with path and file name of materials database"""
    PATH = "hyperspacesim.data.materials"
    MATERIALS_FILE = "materials.json"


class SensorsData(Enum):
    """Enum with path and file name of sensors database"""
    PATH = "hyperspacesim.data.sensors"
    SENSORS_FILE = "sensors.json"


class LightSourceData(Enum):
    """Enum with path and file names of light sources"""
    PATH = "hyperspacesim.data.light_sources"
    SUNLIGHT_SPECTRUM = "wehrli85.spd"


class EarthData(Enum):
    """Enum of path and file names of Earth data"""
    PATH = "hyperspacesim.data.earth_model"
    SOIL_SPECTRUM = "soil.spd"
    OCEAN_SPECTRUM = "ocean.spd"
    MESH = "earth.ply"
    SURFACE_BITMAP = "earth.jpg"


def get_user_data_path(filename):
    """Gets data paths of file in run directory

    Walks through working directory to retrieve file
    path

    Parameters
    ----------
    filename : str
        Name of the file to search for

    Returns
    -------
    str
        Path to file
    """
    for root, _, files in os.walk(Path.cwd()):
        for file in files:
            if file == filename:
                return os.path.join(root, file).replace("\\", "/")

    # raise DataFileNotFoundError(
    #     f"{filename} cannot be found in the case directory"
    # )


def get_kernel_paths():
    """Retrieves all kernel file paths from kernel database

    Returns
    -------
    list
        List of paths to kernel files
    """
    return [
        get_data_path(Kernels.PATH.value, kernel)
        for kernel in Kernels.KERNEL_LIST.value
    ]


def read_json_package_data(path, file):
    """Reads json file

    Parameters
    ----------
    path : str
        Path to file to read
    file : str
        Name of file

    Returns
    -------
    dict
        Contents of json file
    """
    with resources.path(path, file) as path_data:
        with open(path_data, "r", encoding="utf-8") as j:
            return json.loads(j.read())


def get_material_from_database(material_name):
    """Retrieves material dictionary from database

    Parameters
    ----------
    material_name : str
        Name of material in database

    Returns
    -------
    dict
        Material dictionary
    """
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
    """Get unix style path of data

    Parameters
    ----------
    directory : str
        Package location (dot notation) of data as a string
    file : str
        File name of data

    Returns
    -------
    str
        Unix style path to data
    """
    with resources.path(directory, file) as path:
        return str(path).replace("\\", "/")


def get_sunlight_spectrum():
    """Get path to sunlight spectrum data

    Returns
    -------
    str
        Path to sunlight data
    """
    return get_data_path(
        LightSourceData.PATH.value, LightSourceData.SUNLIGHT_SPECTRUM.value
    )


def list_defined_materials():
    """Returns list of materials inside material database

    NOT IMPLEMENTED
    """
    raise NotImplementedError()


def list_defined_sensors():
    """Returns list of sensors in database

    Raises
    ------
    NotImplementedError
        When called
    """
    raise NotImplementedError()


def list_defined_light_sources():
    """Returns list of light sources in database

    Raises
    ------
    NotImplementedError
        When called
    """
    raise NotImplementedError()
