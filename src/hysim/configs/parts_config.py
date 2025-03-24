from __future__ import annotations

from pydantic import Field
from pydantic.dataclasses import dataclass
from typing import Optional, Dict

from hysim.configs.constants import ConfigType


@dataclass(frozen=True)
class Part:
    file: str
    """The mesh file"""
    # TODO validation as these fields are exclusive
    database_material: Optional[str] = Field(default=None)
    user_material: Optional[str] = Field(default=None)


# @dataclass(frozen=True)
class PartsConfig:
    file_type: ConfigType
    parts: Dict[str, Part]
    def __init__(self, file_type: ConfigType):
        self.file_type = file_type
        self.parts = {}

