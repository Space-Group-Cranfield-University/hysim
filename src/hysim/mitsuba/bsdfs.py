"""BSDFs (materials) adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_bsdfs.html#
"""

from typing import Literal, Union

from hysim.mitsuba.abc import MitsubaObject, Discriminator
from hysim.mitsuba.spectra import Spectra


class BSDF(MitsubaObject):
    """Abstract base class for Mitsuba BSDF objects"""

    pass


class DiffuseMaterial(BSDF):
    type: Literal["diffuse"] = "diffuse"
    # filename: str # for texture
    reflectance: Spectra = Discriminator


class RoughConductorMaterial(BSDF):
    type: Literal["roughconductor"] = "roughconductor"
    eta: Spectra = Discriminator
    k: Spectra = Discriminator
    alpha: float


class TwoSidedBRDF(BSDF):
    type: Literal["twosided"] = "twosided"
    material: Union[DiffuseMaterial, RoughConductorMaterial] = Discriminator


# Move to hysim.mitsuba.typing?
BSDFs = Union[DiffuseMaterial, RoughConductorMaterial, TwoSidedBRDF]
