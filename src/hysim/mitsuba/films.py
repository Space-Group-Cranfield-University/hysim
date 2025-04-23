"""Films adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_films.html
"""
from typing import Literal, Iterable

from .abc import MitsubaObject, NamedObjectsMixin
from .spectra import Spectrum as _Spectrum


class Film(MitsubaObject):
    """Abstract base class for Mitsuba film objects"""

    width: int
    height: int
    component_format: str = "float32"


class SpectralFilm(Film, NamedObjectsMixin[_Spectrum]):
    type: Literal["specfilm"] = "specfilm"

    __pydantic_extra__: dict[str, _Spectrum] = {}

    def set_spectrum(self, spectra: Iterable[tuple[str, _Spectrum]]):
        for name, spectrum in spectra:
            self._add_item(name, spectrum)


class HDRFilm(Film):
    type: Literal["hdrfilm"] = "hdrfilm"
