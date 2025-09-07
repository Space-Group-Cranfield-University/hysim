from typing import Optional

from pydantic import NonNegativeFloat, PositiveInt
from pydantic.dataclasses import dataclass

from hysim.util.constants import ConfigType, ImagingMode


@dataclass(frozen=True)
class Camera:
    field_of_view: float
    shutter_time: Optional[NonNegativeFloat] = 0
    frame_count: Optional[PositiveInt] = 1


@dataclass(frozen=True)
class Film:
    width: PositiveInt
    height: PositiveInt


@dataclass(frozen=True)
class SensorConfig:
    file_type: ConfigType
    camera: Camera
    film: Film
    imaging_mode: ImagingMode
    spectrum_file: str
    reference_wavelengths: Optional[list[int]] = None
