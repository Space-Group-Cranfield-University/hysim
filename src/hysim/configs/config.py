import os
import typing
from hysim.configs.case_config import CaseConfig
from hysim.configs.mission_config import MissionConfig
from rickle import BaseRickle
from strenum import StrEnum

file_type = "file_type"
class ConfigType(StrEnum):
    CASE = "case_config"
    MISSION = "mission_config"
    SENSOR = "sensor_config"
    PARTS = "parts_config"
    MATERIAL = "material_config"

class Config:
    case_config: CaseConfig
    mission_config: MissionConfig
    case_directory: str

    def __init__(self, case_directory:str) -> None:
        self.case_directory = case_directory
        for root, _, files in os.walk(self.case_directory):
            for file in files:
                if file.endswith(".yml"):
                    path = os.path.join(root, file)
                    rickle = BaseRickle(path)
                    if rickle[file_type] == ConfigType.CASE:
                        self.case_config = CaseConfig(**rickle.dict())
                    elif rickle[file_type] == ConfigType.MISSION:
                        self.mission_config = MissionConfig(**rickle.dict())
                    else:
                        pass#raise ValueError(f"{rickle[file_type]} is an invalid config type.")
