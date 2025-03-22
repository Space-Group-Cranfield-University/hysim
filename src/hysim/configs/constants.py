from strenum import StrEnum


class ConfigType(StrEnum):
    CASE = "case_config"
    MISSION = "mission_config"
    SENSOR = "sensor_config"
    PARTS = "parts_config"
    MATERIAL = "material_config"
