"""Emitters adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_emitters.html
"""

from hysim.mitsuba.abc import *
from hysim.mitsuba.spectra import Spectrum


class Emitter(NamedMitsubaObject):
    """Abstract base class for Mitsuba emitter objects"""

    pass


class DirectionalEmitter(Emitter):
    to_world: Transform = None
    direction: Vector = None
    irradiance: Spectrum

    @property
    def asdict(self) -> MDict:
        if self.direction is not None:
            return {
                "type": "directional",
                "irradiance": self.irradiance.asdict,
                "direction": self.direction,
            }
        else:
            return {
                "type": "directional",
                "irradiance": self.irradiance.asdict,
                "to_world": self.to_world,
            }
