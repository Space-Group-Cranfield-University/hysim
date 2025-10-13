from pydantic.dataclasses import dataclass

from hysim.mitsuba.integrators import Integrator
from hysim.mitsuba.samplers import Sampler
from hysim.util.constants import ConfigType, OutputFormat, MitsubaVariant


@dataclass(frozen=True)
class OutputItem:
    format: OutputFormat
    # TODO: validate its a directory for png and csv or split export types (OutputItem) into separate classes
    file_name: str


@dataclass(frozen=True)
class CaseConfig:
    file_type: ConfigType
    mitsuba_variant: MitsubaVariant
    output: list[OutputItem]
    integrator: Integrator # = PathTracer(max_depth=-1)
    sampler: Sampler # = StratifiedSampler(sample_count=64)


    @property
    def requires_spectral(self) -> bool:
        return any(o.format != OutputFormat.GIF for o in self.output)

    @property
    def requires_rgb(self) -> bool:
        return any(o.format == OutputFormat.GIF for o in self.output)



