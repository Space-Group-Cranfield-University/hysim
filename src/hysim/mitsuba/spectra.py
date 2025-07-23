"""Spectra adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_spectra.html"""

from typing import Literal, Any, Optional

from pydantic import field_serializer, field_validator

from .abc import MitsubaObject


class Spectrum(MitsubaObject):
    """Abstract base class for Mitsuba spectrum objects"""


class RegularSpectrum(Spectrum):
    type: Literal["regular"] = "regular"
    values: str
    wavelength_min: float
    wavelength_max: float


class IrregularSpectrum(Spectrum):
    type: Literal["irregular"] = "irregular"
    wavelengths: list[float]
    values: list[float]

    @field_validator("wavelengths", "values", mode="before")
    @classmethod
    def _string_to_list(cls, value: Any) -> Any:
        if isinstance(value, str):
            return list(map(float, value.split(",")))
        return value

    @field_serializer("wavelengths", "values")
    def _list_to_string(self, values: list[float]) -> str:
        """Used to match mitsuba format.
        See https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_spectra.html#irregular-spectrum-irregular
        """
        return ", ".join(map(str, values))


class SpdSpectrum(Spectrum):
    type: Literal["spectrum"] = "spectrum"
    filename: str


class UniformSpectrum(Spectrum):
    type: Literal["uniform"] = "uniform"
    value: float
    wavelength_min: Optional[float] = None
    wavelength_max: Optional[float] = None


class RGBSpectrum(Spectrum):
    type: Literal["rgb"] = "rgb"
    value: list[float]  # Len 3

class D65Spectrum(Spectrum):
    type: Literal["d65"] = "d65"
    color: list[float]