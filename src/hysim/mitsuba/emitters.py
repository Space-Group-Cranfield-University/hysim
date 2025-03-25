from hysim.mitsuba.abc import *
from hysim.mitsuba.spectra import Spectrum

class Emitter(NamedMitsubaObject):
    pass

class DirectionalEmitter(Emitter):
    to_world: Transform = None
    # Setting direction forces it to be used over to_world.
    direction: Vector = None
    irradiance: Spectrum
    @property
    def asdict(self) -> MDict:
        if self.direction is not None:
            return {
                "type": "directional",
                "irradiance": self.irradiance.asdict,
                "direction": self.direction
            }
        else:
            return {
                "type": "directional",
                "irradiance": self.irradiance.asdict,
                "to_world": self.to_world
            }
