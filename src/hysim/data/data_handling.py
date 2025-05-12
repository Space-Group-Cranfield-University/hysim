"""Data Handling Module

Contains Database Enums to define data paths and functions to
handle data retrieval.
"""

from functools import cache
from importlib import resources
from enum import Enum
from typing import Any

from hysim.util.strenum import StrEnum

import json

from hysim.mitsuba.bsdfs import TwoSidedBRDF, DiffuseMaterial


# ===== IO Error Handling ===== #
class DataFileNotFoundError(Exception):
    """Exception for handling file not found in database"""


class ConfigFileMissing(Exception):
    """Exception to handle missing configuration file"""


# ===== DATABASE ===== #
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

    SOIL_SPECTRUM = "soil.spd"
    OCEAN_SPECTRUM = "ocean.spd"
    # MESH = "earth.ply"
    SURFACE_BITMAP = "earth.jpg"

    def __new__(cls, file):
        path = "hysim.data.earth_model"
        return str.__new__(cls, get_data_path(path, file))


def kernel_paths():
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


def read_json_package_data(path: str, file: str) -> dict[str, Any]:
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


@cache
def load_material_database() -> dict[str, TwoSidedBRDF]:
    """Loads the material database caches it and returns it as
    a dictionary

    Returns
    -------
    dict[str, TwoSidedBRDF]
        Dictionary of materials
    """
    materials = read_json_package_data(MaterialsData.PATH, MaterialsData.MATERIALS_FILE)
    for material_name, material_dict in materials.items():
        mat = TwoSidedBRDF(**material_dict)
        if isinstance(mat.material, DiffuseMaterial):
            mat.material.reflectance.filename = get_data_path(
                MaterialsData.PATH, mat.material.reflectance.filename
            )
        else:
            raise ValueError(f"Invalid material type for {material_name} in database")
        materials[material_name] = mat
    return materials


def get_database_material(material_name: str) -> TwoSidedBRDF:
    """Retrieves material dictionary from database"""
    material = load_material_database().get(material_name)
    if material is None:
        raise DataFileNotFoundError(f"Material {material_name} not found in database")
    return material


def sun_spectrum_path() -> str:
    return get_data_path(LightSourceData.PATH, LightSourceData.SUNLIGHT_SPECTRUM)


def defined_materials() -> list[str]:
    """Returns list of materials inside material database"""
    materials = load_material_database()
    return list(materials.keys())


def defined_sensors():
    """Returns list of sensors in database

    Raises
    ------
    NotImplementedError
        When called
    """
    raise NotImplementedError()


def defined_light_sources():
    """Returns list of light sources in database

    Raises
    ------
    NotImplementedError
        When called
    """
    raise NotImplementedError()
