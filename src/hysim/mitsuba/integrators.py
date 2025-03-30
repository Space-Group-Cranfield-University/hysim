"""Integrators adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_integrators.html#

"""
from typing import Literal

from pydantic.dataclasses import dataclass

from hysim.mitsuba.abc import *

@dataclass
class Integrator(MitsubaObject):
    """Abstract base class for Mitsuba integrator objects"""

    pass

@dataclass
class PathTracer(Integrator):
    type: Literal["path"] = "path"
    max_depth: int = -1
    rr_depth: int = 5
    hide_emitters: bool = False

    @property
    def asdict(self) -> MDict:
        return {
            "type": self.type,
            "max_depth": self.max_depth,
            "rr_depth": self.rr_depth,
            "hide_emitters": self.hide_emitters,
        }


@dataclass
class DirectIntegrator(Integrator):
    type: Literal["direct"] = "direct"
    hide_emitters: bool = False

    @property
    def asdict(self) -> MDict:
        return {
            "type": self.type,
            "hide_emitters": self.hide_emitters,
        }


Integrators = Union[PathTracer, DirectIntegrator]
