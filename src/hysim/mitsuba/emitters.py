"""Emitters adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_emitters.html
"""

from typing import Optional, Literal

from typing_extensions import Self

from pydantic import model_validator

from .abc import MitsubaObject, Vector, Transform
from .spectra import Spectrum as _Spectrum


class Emitter(MitsubaObject):
    """Abstract base class for Mitsuba emitter objects"""


class DirectionalEmitter(Emitter):
    type: Literal["directional"] = "directional"
    to_world: Optional[Transform] = None
    direction: Optional[Vector] = None
    irradiance: _Spectrum

    @model_validator(mode="after")
    def _mutually_exclusive(self) -> Self:
        if (self.to_world is None and self.direction is None) or (
            self.to_world is not None and self.direction is not None
        ):
            raise ValueError(
                "Either the to_world or direction must be specified, but not both"
            )
        return self


class ConstantEmitter(Emitter):
    type: Literal["constant"] = "constant"
    radiance: _Spectrum
