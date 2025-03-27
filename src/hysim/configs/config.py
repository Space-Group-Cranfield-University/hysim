import os
from typing import Dict, Literal, Set, Iterable

from rickle import BaseRickle

from hysim.configs.case_config import CaseConfig
from hysim.configs.constants import ConfigType
from hysim.configs.materials_config import MaterialsConfig, MaterialWrapper
from hysim.configs.mission_config import MissionConfig
from hysim.configs.sensor_config import SensorConfig
from hysim.configs.parts_config import PartsConfig, Part
from hysim.mitsuba.bsdfs import BSDFs

# TODO: Format exceptions


class Config:
    """Handles input data from input files in case directory

    Processing of files is done internally. Configuration files
    are loaded and placed into their corresponding class.
    """

    _case_config: CaseConfig
    _mission_config: MissionConfig
    _sensor_config: SensorConfig
    _part_config: PartsConfig
    _materials_config: MaterialsConfig

    _case_directory: str
    _directories: Set[str] = set()
    _sensor_spectrum_path: str

    def __init__(self, case_directory: str) -> None:
        # Walk through the case directory and load the configuration files
        self._file_type_ltr: Literal["file_type"] = "file_type"
        self._case_directory = case_directory
        _case_files: Dict[str, str] = {}
        for root, _, files in os.walk(self._case_directory):
            for file in files:
                if file.endswith(".yml"):
                    path = os.path.join(root, file).replace("\\", "/")
                    self._init_configs(path)
                elif file.endswith((".spd", ".ply")):
                    _case_files[file] = os.path.join(root, file).replace("\\", "/")
                    self._directories.add(root.replace("\\", "/"))
        self._sensor_spectrum_path = _case_files[self._sensor_config.spectrum_file]
        self._directories.add(case_directory)


    def _init_configs(self, path: str) -> None:
        rickle = BaseRickle(path)
        file_type = rickle[self._file_type_ltr]
        if file_type == ConfigType.CASE:
            self._case_config = CaseConfig(**rickle.dict())

        elif file_type == ConfigType.MISSION:
            self._mission_config = MissionConfig(**rickle.dict())

        elif file_type == ConfigType.SENSOR:
            self._sensor_config = SensorConfig(**rickle.dict())

        elif file_type == ConfigType.PARTS:
            self._part_config = PartsConfig(file_type)
            for part_name, part_dict in rickle.dict()["components"].items():
                self._part_config.parts[part_name] = Part(**part_dict)

        elif file_type == ConfigType.MATERIAL:
            self._materials_config = MaterialsConfig(file_type)
            for material_name, material_dict in rickle.dict()["materials"].items():
                self._materials_config.materials[material_name] = MaterialWrapper(
                    **material_dict
                ).material
        else:
            raise ValueError(f"{file_type} is an invalid config type at {path}")

    @property
    def case_directory(self) -> str:
        return self._case_directory

    @property
    def sensor_spectrum_path(self) -> str:
        """Returns the path to the sensor spectrum file"""
        return self._sensor_spectrum_path

    @property
    def directories(self) -> Iterable[str]:
        """A set of directories in the user specified case directory that are to be
        added to the mitsuba search path"""
        return self._directories

    @property
    def case(self) -> CaseConfig:
        """Configuration data for the simulation case"""
        return self._case_config

    @property
    def mission(self) -> MissionConfig:
        """Configuration data for the mission parameters"""
        return self._mission_config

    @property
    def sensor(self) -> SensorConfig:
        """Configuration data for the HSI/MSI sensor"""
        return self._sensor_config

    @property
    def parts(self) -> Dict[str, Part]:
        """Configuration data for the target components

        Returns
        -------
        Dict[str, Part]
            A target dictionary of target components, where the key is the name of the
            component and the value is a Part class
        """
        return self._part_config.parts

    @property
    def user_materials(self) -> Dict[str, BSDFs]:
        """Dictionary of user defined materials

        Returns
        -------
        Dict[str, BSDFs]
            A dictionary of user defined materials, where the key is the name of the
            material and the value is a BSDFs class
        """
        return self._materials_config.materials
