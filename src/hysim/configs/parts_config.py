from __future__ import annotations

from pydantic import Field, model_validator
from pydantic.dataclasses import dataclass
from typing import Optional
from typing_extensions import Self

from hysim.configs.constants import ConfigType


@dataclass(frozen=True)
class Part:
    file: str
    """The mesh file"""
    database_material: Optional[str] = Field(default=None)
    user_material: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def mutually_exclusive(self) -> Self:
        if (self.database_material and self.user_material) or (
            not self.database_material and not self.user_material
        ):
            raise ValueError(
                "Either a database_material or a user_material parameter must be specified, but not both."
            )
        return self


@dataclass(frozen=True)
class PartsConfig:
    file_type: ConfigType
    components: dict[str, Part]
