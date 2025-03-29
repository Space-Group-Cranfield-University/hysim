from __future__ import annotations

from pydantic.dataclasses import dataclass

from hysim.configs.constants import ConfigType
from hysim.mitsuba.bsdfs import BSDFs

@dataclass(frozen=True)
class MaterialsConfig:
    file_type: ConfigType
    materials: dict[str, BSDFs]
