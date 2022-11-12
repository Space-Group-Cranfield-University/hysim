"""Module handles user input data in the case directory and provides
an interface for the rest of the package."""
import os
import yaml

# TODO: Add exception handling to configuration file inputs


class Configs:
    """Loads input data from yml files in case directory"""

    valid_config_types = [
        "case_config",
        "mission_config",
        "sensor_config",
        "parts_config",
        "material_config",
    ]

    def __init__(self):
        self.case_config = {}
        self.mission_config = {}
        self.sensor_config = {}
        self.parts_config = {}
        self.additional_materials = {}

    def _append_material_config(self, config_data):
        self.additional_materials.update(config_data["materials"])

    def _sort_config_data(self, file_type, config_data):
        """Assign config data to file type attribute"""

        if file_type not in Configs.valid_config_types:
            raise ValueError(f"{file_type} is an invalid config type.")

        if file_type == "material_config":
            self._append_material_config(config_data)

        else:
            setattr(self, file_type, config_data)

    def _get_config_data(self, file):
        with open(file, "r") as contents:
            config = yaml.safe_load(contents)
        file_type = config["file_type"]
        del config["file_type"]
        return file_type, config

    def load_configs(self, case_directory="."):
        """Walk through case directory and load config files"""
        for root, _, files in os.walk(case_directory):
            for file in files:
                if file.endswith(".yml"):
                    path = os.path.join(root, file)
                    file_type, config_data = self._get_config_data(path)
                    self._sort_config_data(file_type, config_data)
