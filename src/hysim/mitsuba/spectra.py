from hysim.mitsuba.abc import *

class Spectrum(NamedMitsubaObject):
    pass

class IrregularSpectrum(Spectrum):
    wavelengths: str
    values: str
    @property
    def asdict(self) -> MDict:
        return {
            "type" : "irregular",
            "wavelengths" : self.wavelengths,
            "values" : self.values
        }

class SpdSpectrum(Spectrum):
    filename: str
    @property
    def asdict(self) -> MDict:
        return {
            "type": "spectrum",
            "filename": self.filename
        }