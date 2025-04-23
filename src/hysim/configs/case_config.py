from __future__ import annotations
from typing import Optional

from pydantic.dataclasses import dataclass

from hysim.util.constants import ConfigType, OutputFormat, MitsubaVariant
from hysim.mitsuba.integrators import Integrator
from hysim.mitsuba.samplers import Sampler


@dataclass(frozen=True)
class OutputItem:
    format: OutputFormat
    file_name: str
    reference_wavelengths: Optional[list[int]] = None


@dataclass(frozen=True)
class CaseConfig:
    file_type: ConfigType
    mitsuba_variant: MitsubaVariant
    output: list[OutputItem]
    integrator: Integrator # = PathTracer(max_depth=-1)
    sampler: Sampler # = StratifiedSampler(sample_count=64)
