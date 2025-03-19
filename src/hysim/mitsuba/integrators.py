from hysim.mitsuba.abc import *


class Integrator(MitsubaObject):
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
            "hide_emitters": self.hide_emitters
        }
