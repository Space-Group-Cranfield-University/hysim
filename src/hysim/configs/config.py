import logging
from pathlib import Path
from typing import Literal, Set, Iterable, Type, Union

from pydantic import ValidationError
from rickle import BaseRickle

import hysim.data.data_handling as dh
from hysim.configs.case_config import CaseConfig
from hysim.configs.materials_config import MaterialsConfig
from hysim.configs.mission_config import MissionConfig
from hysim.configs.parts_config import PartsConfig, Part
from hysim.configs.sensor_config import SensorConfig
from hysim.mitsuba.bsdfs import BSDF
from hysim.mitsuba.spectra import Spectrum
from hysim.util.constants import ConfigType, ImagingMode, OutputFormat


def _exit_on_error():
    logging.info("Invalid configuration file. Exiting...")
    logging.shutdown()
    import sys
    sys.exit()

def _log_config_error(file_type: str, location: str, message: str, path: str, value: str):
    """Logs a configuration error message

    Parameters
    ----------
    file_type : str
        The type of configuration file
    location : str
        The path to the error in the config file
    message : str
        The error message
    path : str
        The path to the config file
    value : str
        The value that caused the error
    """
    logging.error(
        f'The field "{location}" is invalid in "{path}" (ConfigType: {file_type}).\n'
        f"          {'Reason:'.ljust(10)}{message}\n"
        f"          {'Input:'.ljust(10)}{value}"
    )


class Config:
    """Handles input data from input files in case directory

    Processing of files is done internally. Configuration files
    are loaded and placed into their corresponding class.
    """

    # The values in this dict start as the config class type, but are replaced with the class instance during _init_configs
    _configs: dict[ConfigType, Union[Type, Union[CaseConfig, MissionConfig, SensorConfig, PartsConfig, MaterialsConfig]]] = {
        ConfigType.CASE: CaseConfig,
        ConfigType.MISSION: MissionConfig,
        ConfigType.SENSOR: SensorConfig,
        ConfigType.PARTS: PartsConfig,
        ConfigType.MATERIAL: MaterialsConfig,
    }

    def __init__(self, case_directory: Path):
        logging.info("Getting user inputs from configuration files")
        self._file_type_ltr: Literal["file_type"] = "file_type"
        self._case_directory = case_directory
        self._directories: Set[str] = set()
        case_files: dict[str, str] = {}

        yaml_ext = {".yml", ".yaml" ".json", ".toml"}
        content_ext = {".spd", ".ply"}
        # Walk through the case directory and load the configuration files
        for path in case_directory.rglob("*"):
            if path.suffix in yaml_ext:
                self._init_configs(str(path))
            elif path.suffix in content_ext:
                case_files[path.name] = str(path)
                self._directories.add(str(path.parent))

        # TODO: Things to fail fast:
        #   - User specified spectrum file.
        #   - User materials names are consistent through all config files.
        #   - User part names match files

        # Load spectrum file
        self._sensor_bands = dh.read_spd(case_files[self.sensor.spectrum_file], self.sensor.imaging_mode)

        if (self.sensor.imaging_mode == ImagingMode.MULTISPECTRAL
                and any(x.format == OutputFormat.EXR for x in self.case.output)):
            error_message = None
            input_value = "N/A"
            if self.sensor.reference_wavelengths is None:
                error_message = "Reference wavelengths are required for multispectral imaging"
            elif len(self.sensor.reference_wavelengths) != len(self._sensor_bands):
                error_message = "The number of reference wavelengths must match the number of bands in the spectrum file"
                input_value = str(self.sensor.reference_wavelengths)
            if error_message:
                _log_config_error(
                    ConfigType.SENSOR,
                    "reference_wavelengths",
                    error_message,
                    case_files[self.sensor.spectrum_file],
                    input_value
                )
                _exit_on_error()

        self._directories.add(str(case_directory))

    def _init_configs(self, path: str):
        rickle = BaseRickle(path)
        file_type = rickle[self._file_type_ltr]

        try:
            self._configs[file_type] = self._configs[file_type](**rickle.dict())
        except ValidationError as e:
            for error in e.errors():
                message = error["msg"]
                location = ".".join(map(str, error["loc"]))
                value = error["input"]
                _log_config_error(file_type, location, message, path, value)
            _exit_on_error()
        except KeyError:
            logging.error(f'"%s" is an invalid config type at "%s"', file_type, path)
            _exit_on_error()

    @property
    def case_directory(self) -> Path:
        return self._case_directory

    @property
    def sensor_bands(self) -> list[tuple[str, Spectrum]]:
        """Returns the sensor band sensitivity"""
        return self._sensor_bands

    @property
    def directories(self) -> Iterable[str]:
        """A set of directories in the user specified case directory that are to be
        added to the mitsuba search path"""
        return self._directories

    @property
    def case(self) -> CaseConfig:
        """Configuration data for the simulation case"""
        return self._configs[ConfigType.CASE]

    @property
    def mission(self) -> MissionConfig:
        """Configuration data for the mission parameters"""
        return self._configs[ConfigType.MISSION]

    @property
    def sensor(self) -> SensorConfig:
        """Configuration data for the HSI/MSI sensor"""
        return self._configs[ConfigType.SENSOR]

    @property
    def parts(self) -> dict[str, Part]:
        """Configuration data for the target components

        Returns
        -------
        dict[str, Part]
            A target dictionary of target components, where the key is the name of the
            component and the value is a Part class
        """
        return self._configs[ConfigType.PARTS].components

    @property
    def user_materials(self) -> dict[str, BSDF]:
        """Dictionary of user defined materials

        Returns
        -------
        dict[str, BSDFs]
            A dictionary of user defined materials, where the key is the name of the
            material and the value is a BSDFs class
        """
        return self._configs[ConfigType.MATERIAL].materials
