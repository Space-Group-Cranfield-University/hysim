from __future__ import annotations

from typing import Dict

from pydantic.dataclasses import dataclass

from hysim.configs.constants import ConfigType
from hysim.mitsuba.bsdfs import BSDFs


@dataclass
class MaterialWrapper:
    material: BSDFs


class MaterialsConfig:
    file_type: ConfigType
    materials: Dict[str, BSDFs]

    def __init__(self, file_type: ConfigType):
        self.file_type = file_type
        self.materials = {}
