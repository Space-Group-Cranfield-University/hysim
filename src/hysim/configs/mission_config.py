from typing import Union, Literal, TypeVar
from typing_extensions import Self

from pydantic import field_validator, model_validator, ValidationInfo
from pydantic.dataclasses import dataclass
from hysim.util.constants import ConfigType, PositionFormat

_T = TypeVar("_T")


@dataclass(frozen=True)
class Satellite:
    position_frame: PositionFormat  # TODO: rename position_frame to position_format
    position: list[Union[float, str]]
    attitude: list[float]

    @field_validator("position", mode="after")
    @classmethod
    def _validate_position(cls, value: list[Union[float, str]], info: ValidationInfo) -> list[Union[float, str]]:
        if info.data["position_frame"] == PositionFormat.TLE:
            if len(value) != 2 or not all(isinstance(v, str) for v in value):
                raise ValueError("The TLE position must be a list of two strings.")
            return value

        if len(value) != 6 or not all(isinstance(v, float) for v in value):
            raise ValueError("The list length must be 6")
        return value


@dataclass(frozen=True)
class Target(Satellite):
    @field_validator("position_frame", mode="after")
    @classmethod
    def _validate_position_frame(cls, value: PositionFormat) -> PositionFormat:
        if value == PositionFormat.STATE_LVLH:
            raise ValueError("The target satellite cannot be in the LVLH frame.")
        return value


@dataclass(frozen=True)
class Chaser(Satellite):
    attitude: Union[list[float], Literal["lookat"]]
    @property
    def is_lookat(self) -> bool:
        return self.attitude == "lookat"


@dataclass(frozen=True)
class MissionConfig:
    file_type: ConfigType
    datetime: str
    target: Target
    chaser: Chaser

    @model_validator(mode="after")
    def _validate_frames(self) -> Self:
        t = self.target.position_frame
        c = self.chaser.position_frame
        if (t == PositionFormat.KEPLERIAN and c == PositionFormat.TLE) or (
            t == PositionFormat.TLE and c == PositionFormat.KEPLERIAN
        ):
            raise ValueError("TLE and Keplerian formats are not compatible.")
        return self
