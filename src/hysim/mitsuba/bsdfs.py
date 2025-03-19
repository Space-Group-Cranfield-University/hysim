"""BSDFs or Materials adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_bsdfs.html#"""
from hysim.mitsuba.abc import *
from hysim.mitsuba.spectra import Spectrum


class BSDF(NamedMitsubaObject):
    pass


class DiffuseMaterial(BSDF):
    reflectance: Spectrum
    # filename: str # for texture

    @property
    def asdict(self) -> MDict:
        return {
            "type": "diffuse",
            "reflectance": self.reflectance.asdict
        }


class TwoSidedBRDF(MitsubaObject):
    bsdf: BSDF

    @property
    def asdict(self) -> MDict:
        return {
            "type": "twosided",
            "material": self.bsdf.asdict
        }
