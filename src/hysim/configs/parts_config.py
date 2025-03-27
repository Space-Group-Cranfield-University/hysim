from __future__ import annotations

from pydantic import Field, model_validator
from pydantic.dataclasses import dataclass
from typing import Optional, Dict

from hysim.configs.constants import ConfigType


@dataclass(frozen=True)
class Part:
    file: str
    """The mesh file"""
    database_material: Optional[str] = Field(default=None)
    user_material: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def validate_materials(self):
        if self.database_material and self.user_material:
            raise ValueError(
                "A part cannot have both a database_material and a user_material parameter"
            )
        return self


class PartsConfig:
    file_type: ConfigType
    parts: Dict[str, Part]

    def __init__(self, file_type: ConfigType):
        self.file_type = file_type
        self.parts = {}
