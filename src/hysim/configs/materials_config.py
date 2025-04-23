from pydantic.dataclasses import dataclass

from hysim.util.constants import ConfigType
from hysim.mitsuba.bsdfs import BSDF


@dataclass(frozen=True)
class MaterialsConfig:
    file_type: ConfigType
    materials: dict[str, BSDF]
