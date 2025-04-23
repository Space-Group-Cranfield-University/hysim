"""Samplers adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_samplers.html"""
from typing import Literal

from .abc import MitsubaObject


class Sampler(MitsubaObject):
    sample_count: int


class StratifiedSampler(Sampler):
    type: Literal["stratified"] = "stratified"


class IndependentSampler(Sampler):
    type: Literal["independent"] = "independent"


class MultiJitterSampler(Sampler):
    type: Literal["multijitter"] = "multijitter"
