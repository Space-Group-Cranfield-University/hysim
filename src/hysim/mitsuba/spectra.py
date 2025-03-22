from hysim.mitsuba.abc import *
from pydantic.dataclasses import dataclass


@dataclass
class Spectrum(NamedMitsubaObject):
    pass


@dataclass
class IrregularSpectrum(Spectrum):
    wavelengths: str
    values: str

    @property
    def asdict(self) -> MDict:
        return {
            "type": "irregular",
            "wavelengths": self.wavelengths,
            "values": self.values,
        }


@dataclass
class SpdSpectrum(Spectrum):
    filename: str

    @property
    def asdict(self) -> MDict:
        return {"type": "spectrum", "filename": self.filename}


Spectra = Union[IrregularSpectrum, SpdSpectrum]  # create_type_alias(Spectrum)
