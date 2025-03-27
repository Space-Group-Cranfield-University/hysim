"""Integrators adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_integrators.html#

"""

from hysim.mitsuba.abc import *


class Integrator(MitsubaObject):
    """Abstract base class for Mitsuba integrator objects"""

    pass


class PathTracer(Integrator):
    max_depth: int = -1
    rr_depth: int = 5
    hide_emitters: bool = False

    @property
    def asdict(self) -> MDict:
        return {
            "type": "path",
            "max_depth": self.max_depth,
            "rr_depth": self.rr_depth,
            "hide_emitters": self.hide_emitters,
        }


# Integrators = Union[PathTracer]
