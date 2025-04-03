"""Spectra adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_spectra.html"""
from typing import Literal, Union, Any

from pydantic import field_serializer, field_validator

from hysim.mitsuba.abc import MitsubaObject


class Spectrum(MitsubaObject):
    """Abstract base class for Mitsuba spectrum objects"""

    pass


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


Spectra = Union[IrregularSpectrum, SpdSpectrum]  # create_type_alias(Spectrum)
