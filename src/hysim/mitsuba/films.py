from hysim.mitsuba.abc import *
from hysim.mitsuba.abc import _iterate_named_objects
from hysim.mitsuba.spectra import Spectrum


class Film(MitsubaObject):
    """Abstract base class for Mitsuba Film objects"""
    width: int = 768
    height: int = 576
    component_format: str = "float32"

    @property
    @abstractmethod
    def asdict(self) -> MDict:
        return {
            "type": None,
            "width": self.width,
            "height": self.height,
            "component_format": self.component_format,
        }


class  SpectralFilm(Film):
    spectra: List[Spectrum]

    @property
    def asdict(self) -> MDict:
        d = super().asdict
        d["type"] = "specfilm"
        _iterate_named_objects(d, self.spectra, "band")
        return d
