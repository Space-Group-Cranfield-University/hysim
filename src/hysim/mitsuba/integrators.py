"""Integrators adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_integrators.html#

"""

from typing import Literal, Union

from hysim.mitsuba.abc import MitsubaObject


class Integrator(MitsubaObject):
    """Abstract base class for Mitsuba integrator objects"""

    pass


class PathTracer(Integrator):
    type: Literal["path"] = "path"
    max_depth: int = -1
    rr_depth: int = 5
    hide_emitters: bool = False


class DirectIntegrator(Integrator):
    type: Literal["direct"] = "direct"
    hide_emitters: bool = False


Integrators = Union[PathTracer, DirectIntegrator]
