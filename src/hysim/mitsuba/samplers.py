"""Adpated from: https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_samplers.html"""
from hysim.mitsuba.abc import *


class Sampler(MitsubaObject):
    sample_count: int

    @property
    @abstractmethod
    def asdict(self) -> MDict:
        return {
            "type": None,
            "sample_count": self.sample_count
        }


class StratifiedSampler(Sampler):
    @property
    def asdict(self) -> MDict:
        d = super().asdict
        d["type"] = "stratified"
        return d
