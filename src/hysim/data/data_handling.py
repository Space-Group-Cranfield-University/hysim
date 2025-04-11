"""Data Handling Module

Contains Database Enums to define data paths and functions to
handle data retrieval.
"""
import functools
from importlib import resources
from enum import Enum

from strenum import StrEnum

import json

from hysim.mitsuba.bsdfs import TwoSidedBRDF


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
    PATH = "hysim.data.kernels"
    KERNEL_LIST = ["de440s.bsp", "geophysical.ker", "naif0012.tls", "gm_de440.tpc"]


class MaterialsData(StrEnum):
    """Enum with path and file name of materials database"""
    PATH = "hysim.data.materials"
    MATERIALS_FILE = "materials.json"


class SensorsData(Enum):
    """Enum with path and file name of sensors database"""
    PATH = "hysim.data.sensors"
    SENSORS_FILE = "sensors.json"


class LightSourceData(StrEnum):
    """Enum with path and file names of light sources"""
    PATH = "hysim.data.light_sources"
    SUNLIGHT_SPECTRUM = "wehrli85.spd"


class EarthData(StrEnum):
    """Enum of path and file names of Earth data"""
    PATH = "hysim.data.earth_model"
    SOIL_SPECTRUM = "soil.spd"
    OCEAN_SPECTRUM = "ocean.spd"
    MESH = "earth.ply"
    SURFACE_BITMAP = "earth.jpg"


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

@functools.cache
def load_material_database() -> dict[str, TwoSidedBRDF]:
    """Loads the material database caches it and returns it as
    a dictionary

    Returns
    -------
    dict[str, TwoSidedBRDF]
        Dictionary of materials
    """
    materials = read_json_package_data(
        MaterialsData.PATH, MaterialsData.MATERIALS_FILE
    )
    for material_name, material_dict in materials.items():
        mat = TwoSidedBRDF(**material_dict)
        mat.material.reflectance.filename = get_data_path(
            MaterialsData.PATH, mat.material.reflectance.filename
        )
        materials[material_name] = mat
    return materials


def get_database_material(material_name: str) -> TwoSidedBRDF:
    """Retrieves material dictionary from database"""
    return load_material_database()[material_name]

def get_data_path(directory: str, file: str) -> str:
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
        Path to data
    """
    with resources.path(directory, file) as path:
        return str(path)


def get_earth_mesh_path() -> str:
    return get_data_path(EarthData.PATH,EarthData.MESH)

def get_ocean_spectrum_path() -> str:
    return get_data_path(EarthData.PATH,EarthData.OCEAN_SPECTRUM)

def get_sun_spectrum_path() -> str:
    return get_data_path(LightSourceData.PATH, LightSourceData.SUNLIGHT_SPECTRUM)

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