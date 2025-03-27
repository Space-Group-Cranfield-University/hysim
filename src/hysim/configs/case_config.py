from __future__ import annotations

from typing import Optional

from pydantic.dataclasses import dataclass

from hysim.configs.constants import ConfigType, OutputFormat, MitsubaVariant


@dataclass(frozen=True)
class Sampler:
    type: str
    sample_count: int


@dataclass(frozen=True)
class Integrator:
    type: str
    max_depth: int


@dataclass(frozen=True)
class OutputItem:
    format: OutputFormat
    file_name: str
    reference_wavelengths: Optional[list[int]] = None


@dataclass(frozen=True)
class CaseConfig:
    file_type: ConfigType
    mitsuba_variant: MitsubaVariant
    sampler: Sampler
    integrator: Integrator
    output: list[OutputItem]
