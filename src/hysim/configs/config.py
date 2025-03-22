import os
from typing import Dict, Literal

from pydantic import TypeAdapter
from rickle import BaseRickle

from hysim.configs.case_config import CaseConfig
from hysim.configs.constants import ConfigType
from hysim.configs.materials_config import MaterialsConfig, MaterialWrapper
from hysim.configs.mission_config import MissionConfig
from hysim.configs.sensor_config import SensorConfig
from hysim.configs.parts_config import PartsConfig, Part
from hysim.mitsuba.bsdfs import BSDFs


class Config:
    _case_config: CaseConfig
    _mission_config: MissionConfig
    _sensor_config: SensorConfig
    _part_config: PartsConfig
    _materials_config: MaterialsConfig
    _case_directory: str

    def __init__(self, case_directory: str) -> None:
        self._file_type: Literal["file_type"] = "file_type"
        self._case_directory = case_directory
        for root, _, files in os.walk(self._case_directory):
            for file in files:
                if file.endswith(".yml"):
                    path = os.path.join(root, file)  # TODO: replace with pathlib
                    self._init_configs(path)

    def _init_configs(self, path: str) -> None:
        # Make this a dictionary instead
        rickle = BaseRickle(path)
        if rickle[self._file_type] == ConfigType.CASE:
            self._case_config = CaseConfig(**rickle.dict())
        elif rickle[self._file_type] == ConfigType.MISSION:
            self._mission_config = MissionConfig(**rickle.dict())
        elif rickle[self._file_type] == ConfigType.SENSOR:
            self._sensor_config = SensorConfig(**rickle.dict())
        elif rickle[self._file_type] == ConfigType.PARTS:
            self._part_config = PartsConfig(ConfigType.PARTS)
            for part_name, part_dict in rickle.dict()["components"].items():
                self._part_config.parts[part_name] = Part(**part_dict)
        elif rickle[self._file_type] == ConfigType.MATERIAL:
            self._materials_config = MaterialsConfig(ConfigType.MATERIAL)
            for material_name, material_dict in rickle.dict()["materials"].items():
                self._materials_config.materials[material_name] = MaterialWrapper(
                    **material_dict
                ).material
            # a = TypeAdapter(MaterialWrapper).validate_python(rickle.dict()["materials"]["aluminized_mli"])
        else:
            raise ValueError(f"{rickle[self._file_type]} is an invalid config type.")

    @property
    def case_directory(self) -> str:
        return self._case_directory

    @property
    def case(self) -> CaseConfig:
        return self._case_config

    @property
    def mission(self) -> MissionConfig:
        return self._mission_config

    @property
    def sensor(self) -> SensorConfig:
        return self._sensor_config

    @property
    def parts(self) -> Dict[str, Part]:
        return self._part_config.parts

    @property
    def user_materials(self)  -> Dict[str, BSDFs]:
        return self._materials_config.materials
