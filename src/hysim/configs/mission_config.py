from __future__ import annotations

from typing import Union, Literal, Generic, TypeVar

from pydantic import computed_field
from pydantic.dataclasses import dataclass
from hysim.util.constants import ConfigType, PositionFormat

_T = TypeVar("_T")
@dataclass(frozen=True)
class Spacecraft(Generic[_T]):
    position_frame: PositionFormat # TODO: rename position_frame to position_format
    position: list[Union[float, str]]
    attitude: _T

@dataclass(frozen=True)
class TargetSpacecraft(Spacecraft[list[float]]):
    pass


@dataclass(frozen=True)
class ChaserSpacecraft(Spacecraft[Union[list[float], Literal["lookat"]]]):
    is_lvlh: bool

    @computed_field
    @property
    def is_lookat(self) -> bool:
        return self.attitude == "lookat"


@dataclass(frozen=True)
class MissionConfig:
    file_type: ConfigType
    datetime: str
    target: TargetSpacecraft
    chaser: ChaserSpacecraft
