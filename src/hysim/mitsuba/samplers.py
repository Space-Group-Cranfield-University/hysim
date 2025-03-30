"""Samplers adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_samplers.html"""

from typing import Literal

from pydantic.dataclasses import dataclass

from hysim.mitsuba.abc import *

@dataclass
class Sampler(MitsubaObject):
    sample_count: int
    type: str

    def _asdict(self) -> MDict:
        return {
            "type": self.type,
            "sample_count": self.sample_count,
        }

@dataclass
class StratifiedSampler(Sampler):
    type: Literal["stratified"] = "stratified"

    @property
    def asdict(self) -> MDict:
        return self._asdict()


@dataclass
class IndependentSampler(Sampler):
    type: Literal["independent"] = "independent"

    @property
    def asdict(self) -> MDict:
        return self._asdict()


@dataclass
class MultiJitterSampler(Sampler):
    type: Literal["multijitter"] = "multijitter"

    @property
    def asdict(self) -> MDict:
        return self._asdict()


Samplers = Union[StratifiedSampler, IndependentSampler, MultiJitterSampler]
