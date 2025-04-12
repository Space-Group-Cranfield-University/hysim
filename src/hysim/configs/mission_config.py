from __future__ import annotations

from typing import Union, Literal

from pydantic import computed_field
from pydantic.dataclasses import dataclass
from hysim.configs.constants import ConfigType, PositionFormat


@dataclass(frozen=True)
class Spacecraft:
    position_frame: PositionFormat # TODO: rename position_frame to position_format
    position: list[Union[float, str]]
    attitude: list[float]


# class TargetSpacecraft(Spacecraft):
#     pass


@dataclass(frozen=True)
class ChaserSpacecraft(Spacecraft):
    attitude: Union[list[float], Literal["lookat"]]
    is_lvlh: bool

    @computed_field
    @property
    def is_lookat(self) -> bool:
        return self.attitude == "lookat"


@dataclass(frozen=True)
class MissionConfig:
    file_type: ConfigType
    datetime: str
    target: Spacecraft
    chaser: ChaserSpacecraft
