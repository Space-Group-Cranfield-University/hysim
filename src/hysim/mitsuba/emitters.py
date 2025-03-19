from hysim.mitsuba.abc import *
from hysim.mitsuba.spectra import Spectrum

class Emitter(NamedMitsubaObject):
    pass

class DirectionalEmitter(Emitter):
    to_world: Transform
    # Setting direction forces it to be used over to_world.
    direction: Vector
    irradiance: Spectrum
    @property
    def asdict(self) -> MDict:
        if self.direction:
            return {
                "type": "directional",
                "radiance": self.irradiance.asdict,
                "direction": self.direction
            }
        else:
            return {
                "type": "directional",
                "radiance": self.irradiance.asdict,
                "to_world": self.to_world
            }
