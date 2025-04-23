from typing import Union, Literal, Generic, TypeVar
from typing_extensions import Self

from pydantic import field_validator, model_validator
from pydantic.dataclasses import dataclass
from hysim.util.constants import ConfigType, PositionFormat

_T = TypeVar("_T")


@dataclass(frozen=True)
class Spacecraft(Generic[_T]):
    position_frame: PositionFormat  # TODO: rename position_frame to position_format
    position: list[Union[float, str]]
    attitude: _T


@dataclass(frozen=True)
class TargetSpacecraft(Spacecraft[list[float]]):

    @field_validator("position_frame", mode="after")
    @classmethod
    def _validate_position_frame(cls, value: PositionFormat) -> PositionFormat:
        if value == PositionFormat.STATE_LVLH:
            raise ValueError("The target spacecraft cannot be in the LVLH frame.")
        return value


@dataclass(frozen=True)
class ChaserSpacecraft(Spacecraft[Union[list[float], Literal["lookat"]]]):

    @property
    def is_lookat(self) -> bool:
        return self.attitude == "lookat"


@dataclass(frozen=True)
class MissionConfig:
    file_type: ConfigType
    datetime: str
    target: TargetSpacecraft
    chaser: ChaserSpacecraft

    @model_validator(mode="after")
    def _validate_frames(self) -> Self:
        t = self.target.position_frame
        c = self.chaser.position_frame
        if (t == PositionFormat.KEPLERIAN and c == PositionFormat.TLE) or (
            t == PositionFormat.TLE and c == PositionFormat.KEPLERIAN
        ):
            raise ValueError("TLE and Keplerian formats are not compatible.")
        return self
