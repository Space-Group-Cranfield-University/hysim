"""BSDFs or Materials adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_bsdfs.html#"""
from hysim.mitsuba.abc import *
from hysim.mitsuba.spectra import Spectra
from pydantic.dataclasses import dataclass


@dataclass
class BSDF(NamedMitsubaObject):
    pass


@dataclass
class DiffuseMaterial(BSDF):
    reflectance: Spectra
    # filename: str # for texture

    @property
    def asdict(self) -> MDict:
        return {
            "type": "diffuse",
            "reflectance": self.reflectance.asdict,
        }


@dataclass
class RoughConductorMaterial(BSDF):
    eta: Spectra
    k: Spectra
    alpha: float

    @property
    def asdict(self) -> MDict:
        return {
            "type": "roughconductor",
            "eta": self.eta.asdict,
            "k": self.k.asdict,
            "alpha": self.alpha,
        }


@dataclass
class TwoSidedBRDF(BSDF):
    bsdf: BSDF

    @property
    def asdict(self) -> MDict:
        return {
            "type": "twosided",
            "material": self.bsdf.asdict,
        }


BSDFs = Union[DiffuseMaterial, RoughConductorMaterial, TwoSidedBRDF] # create_type_alias(BSDF)

print(BSDFs)