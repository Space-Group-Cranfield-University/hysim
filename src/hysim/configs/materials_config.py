from pydantic.dataclasses import dataclass

from hysim.mitsuba.bsdfs import BSDF
from hysim.util.constants import ConfigType


@dataclass(frozen=True)
class MaterialsConfig:
    file_type: ConfigType
    materials: dict[str, BSDF]
