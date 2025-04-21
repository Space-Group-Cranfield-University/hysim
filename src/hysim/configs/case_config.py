from __future__ import annotations

from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from hysim.util.constants import ConfigType, OutputFormat, MitsubaVariant
from hysim.mitsuba.integrators import Integrators
from hysim.mitsuba.samplers import Samplers


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
    integrator: Integrators = Field(discriminator="type") # = PathTracer(max_depth=-1)
    sampler: Samplers = Field(discriminator="type")  # = StratifiedSampler(sample_count=64)
