from __future__ import annotations

from typing import Optional

from pydantic.dataclasses import dataclass

from hysim.configs.constants import ConfigType, ImagingMode


@dataclass(frozen=True)
class Camera:
    field_of_view: float
    shutter_time: Optional[float] = 0
    frame_count: Optional[int] = 1


@dataclass(frozen=True)
class Film:
    width: int
    height: int


@dataclass(frozen=True)
class SensorConfig:
    file_type: ConfigType
    camera: Camera
    film: Film
    imaging_mode: ImagingMode
    spectrum_file: str
