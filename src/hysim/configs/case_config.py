from pathlib import Path
from typing import Optional, ClassVar, Literal

from pydantic import field_validator, BaseModel
from pydantic.dataclasses import dataclass

from hysim.mitsuba.integrators import Integrator
from hysim.mitsuba.samplers import Sampler
from hysim.util.constants import ConfigType, MitsubaVariant


class OutputItem(BaseModel):
    # format: OutputFormat
    path: Path
    overwrite: bool = False

    @field_validator("path",mode="after")
    @classmethod
    def _path_validator(cls, value: Path):
        expected_path_extension = {
            EXROutput: ".exr",
            PNGOutput: "",
            CSVOutput: "",
            GIFOutput: ".gif"
        }
        ext = expected_path_extension[cls]
        if value.suffix != ext:
            if ext == "":
                raise ValueError(f"{value} must be a directory for {cls.ext} outputs")
            else:
                raise ValueError(f"{value} must have the extension '{ext}'")
        return value



class EXROutput(OutputItem):
    ext: ClassVar[Literal[".exr"]] = ".exr"
    frames: bool = False # Include individual frames


class PNGOutput(OutputItem):
    ext: ClassVar[Literal[".png"]] = ".png"
    # format: OutputFormat = OutputFormat.PNG
    # individual_frames: bool = False
    # name_format : str
    # prefix: str
    pass

class CSVOutput(OutputItem):
    ext: ClassVar[Literal[".csv"]] = ".csv"
    #format: OutputFormat = OutputFormat.CSV
    pass


class GIFOutput(OutputItem):
    ext: ClassVar[Literal[".gif"]] = ".gif"
    # format: OutputFormat = OutputFormat.GIF
    frame_duration: Optional[int] = None # Milliseconds
    frames: bool = False # Include individual frames


@dataclass(frozen=True)
class Output:
    exr: Optional[EXROutput] = None
    png: Optional[PNGOutput] = None
    csv: Optional[CSVOutput] = None
    gif: Optional[GIFOutput] = None

    @property
    def requires_spectral(self) -> bool:
        return any(o is not None for o in (self.exr, self.csv, self.png))

    @property
    def requires_rgb(self) -> bool:
        return self.gif is not None

@dataclass(frozen=True)
class CaseConfig:
    file_type: ConfigType
    mitsuba_variant: MitsubaVariant
    output: Output
    integrator: Integrator # = PathTracer(max_depth=-1)
    sampler: Sampler # = StratifiedSampler(sample_count=64)
