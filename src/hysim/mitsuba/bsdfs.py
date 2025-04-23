"""BSDFs (materials) adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_bsdfs.html#
"""
from typing import Union, Literal

from .abc import MitsubaObject
from .spectra import Spectrum as _Spectrum
from .textures import Texture as _Texture


class BSDF(MitsubaObject):
    """Abstract base class for Mitsuba BSDF objects"""


class DiffuseMaterial(BSDF):
    type: Literal["diffuse"] = "diffuse"
    reflectance: Union[_Spectrum, _Texture]


class RoughConductorMaterial(BSDF):
    type: Literal["roughconductor"] = "roughconductor"
    eta: _Spectrum
    k: _Spectrum
    alpha: float


class TwoSidedBRDF(BSDF):
    type: Literal["twosided"] = "twosided"
    material: BSDF


class BlendedMaterial(BSDF):
    type: Literal["blendbsdf"] = "blendbsdf"
    weight: Union[float, _Texture]
    bsdf_0: BSDF
    bsdf_1: BSDF
