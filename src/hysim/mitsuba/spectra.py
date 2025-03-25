from hysim.mitsuba.abc import *
from pydantic.dataclasses import dataclass


@dataclass
class Spectrum(NamedMitsubaObject):
    pass


@dataclass
class IrregularSpectrum(Spectrum):
    wavelengths: list[float]
    values: list[float]

    @property
    def asdict(self) -> MDict:
        return {
            "type": "irregular",
            "wavelengths": self._iterable_to_string(self.wavelengths),
            "values": self._iterable_to_string(self.values),
        }

    @staticmethod
    def _iterable_to_string(values: Iterable[float]) -> str:
        """Used to match mitsuba format.
        See https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_spectra.html#irregular-spectrum-irregular
        """
        return ", ".join(map(str, values))


@dataclass
class SpdSpectrum(Spectrum):
    filename: str

    @property
    def asdict(self) -> MDict:
        return {
            "type": "spectrum",
            "filename": self.filename,
        }


Spectra = Union[IrregularSpectrum, SpdSpectrum]  # create_type_alias(Spectrum)
