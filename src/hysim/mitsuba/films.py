"""Films adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_films.html
"""
from typing import Literal, Iterable, Union, Annotated

from hysim.mitsuba.abc import MitsubaObject, NamedObjectsMixin, Discriminator
from hysim.mitsuba.spectra import Spectra


class Film(MitsubaObject):
    """Abstract base class for Mitsuba film objects"""

    width: int
    height: int
    component_format: str = "float32"


class SpectralFilm(Film, NamedObjectsMixin[Spectra]):
    type: Literal["specfilm"] = "specfilm"

    __pydantic_extra__ = dict[str, Annotated[Spectra, Discriminator]]

    def set_spectrum(self, spectra: Iterable[tuple[str, Spectra]]):
        for name, spectrum in spectra:
            self._add_item(name, spectrum)


class HDRFilm(Film):
    type: Literal["hdrfilm"] = "hdrfilm"


Films = Union[SpectralFilm, HDRFilm]
