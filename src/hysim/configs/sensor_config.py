from __future__ import annotations
from pydantic.dataclasses import dataclass

@dataclass(frozen=True)
class Camera:
    field_of_view: float
    # shutter_time: float


@dataclass(frozen=True)
class Film:
    width: int
    height: int


@dataclass(frozen=True)
class SensorConfig:
    file_type: str
    camera: Camera
    film: Film
    imaging_mode: str
    spectrum_file: str
    # def __post_init__(self):
    #     self.file_type = ConfigType(self.file_type)
