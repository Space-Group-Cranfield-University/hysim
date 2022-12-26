""" Input Data module

Module handles user input data in the case directory and provides
an interface for the rest of the package to access the data.
"""
import os
import yaml

# TODO: Add exception handling to configuration file inputs


class Configs:
    """Handles input data from yml files in case directory

    Processing of files is done internally. Configuration files
    are loaded from yml files and accessed as dictionaries.

    Attributes
    ----------
    valid_config_types : list
        List of valid config file types
    case_config : dict
        Configuration data for the simulation case
    mission_config : dict
        Configuration data for the mission parameters
    sensor_config : dict
        Configuration data for the HSI/MSI sensor
    parts_config : dict
        Configuration data for the target components
    additional_materials : dict
        Dictionary of user defined materials


    Methods
    -------
    _append_material_config(config_data)
        Adds material to collection of user defined materials
    _sort_config_data(file_type, config_data)
        Sorts config data and places data in corresponding attribute
    _get_config_data(file)
        Reads contents of yaml
    load_configs(case_directory = ".")
        Walks through case directory and reads configuration files.
    """

    valid_config_types = [
        "case_config",
        "mission_config",
        "sensor_config",
        "parts_config",
        "material_config",
    ]

    def __init__(self):
        """Initializer"""
        self.case_config = {}
        self.mission_config = {}
        self.sensor_config = {}
        self.parts_config = {}
        self.additional_materials = {}

    def _append_material_config(self, config_data: dict):
        """Adds material to collection of user defined materials

        Parameters
        ----------
        config_data : dict
            Data read from configuration file
        """
        self.additional_materials.update(config_data["materials"])

    def _sort_config_data(self, file_type: str, config_data: dict):
        """Sorts config data and places data in corresponding attribute

        Parameters
        ----------
        file_type : str
            Type of configuration file
        config_data : dict
            Data read from configuration file

        Raises
        ------
        ValueError
            If the configuration file type is not recognised
        """

        if file_type not in Configs.valid_config_types:
            raise ValueError(f"{file_type} is an invalid config type.")

        if file_type == "material_config":
            self._append_material_config(config_data)

        else:
            setattr(self, file_type, config_data)

    def _get_config_data(self, file):
        """Reads contents of yaml file

        Parameters
        ----------
        file : str
            Path to yaml file

        Returns
        -------
        file_type : str
            Type of configuration file (as defined in file)
        config : dict
            Data contained in yaml file
        """
        with open(file, "r") as contents:
            config = yaml.safe_load(contents)
        file_type = config["file_type"]
        del config["file_type"]
        return file_type, config

    def load_configs(self, case_directory="."):
        """Walks through case directory and reads configuration files

        Parameters
        ----------
        case_directory : str, optional
            Path from run directory to root of case directory, by default "."
            (default assumes case directory is run directory)
        """
        for root, _, files in os.walk(case_directory):
            for file in files:
                if file.endswith(".yml"):
                    path = os.path.join(root, file)
                    file_type, config_data = self._get_config_data(path)
                    self._sort_config_data(file_type, config_data)
