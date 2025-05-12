from pydantic import model_validator
from pydantic.dataclasses import dataclass
from typing import Optional, Literal
from typing_extensions import Self

from hysim.util.constants import ConfigType
from hysim.data import data_handling as dh

@dataclass(frozen=True)
class Part:
    file: str
    """The mesh file"""
    database_material: Optional[Literal[tuple(dh.defined_materials())]] = None
    user_material: Optional[str] = None

    @model_validator(mode="after")
    def _mutually_exclusive(self) -> Self:
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
