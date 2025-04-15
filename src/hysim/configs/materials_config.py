from __future__ import annotations

from typing import Annotated

from pydantic.dataclasses import dataclass

from hysim.configs.constants import ConfigType
from hysim.mitsuba.bsdfs import BSDFs
from hysim.mitsuba.abc import Discriminator


@dataclass(frozen=True)
class MaterialsConfig:
    file_type: ConfigType
    materials: dict[str, Annotated[BSDFs, Discriminator]]
