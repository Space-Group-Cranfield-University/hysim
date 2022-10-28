'''Module handles user input data in the case directory and provides
an interface for the rest of the package.'''
import os
import yaml


class Configs:
    '''Loads input data from yml files in case directory'''
    valid_config_types = [
        "case_config",
        "mission_config",
        "sensor_config",
        "parts_config",
        "material_config"
    ]

    def __init__(self):
        self.case_config = {}
        self.mission_config = {}
        self.sensor_config = {}
        self.parts_config = {}
        self.additional_materials = []

    def _sort_config_data(self, config_data):
        '''Assign config data to file type attribute'''
        try:
            config_data[0] is Configs.valid_config_types
        except ValueError:
            print(config_data[0] + "is not a valid file type.")

        if config_data[0] == "case_config":
            self.case_config = config_data[1]

        if config_data[0] == "mission_config":
            self.mission_config = config_data[1]

        if config_data[0] == "sensor_config":
            self.sensor_config = config_data[1]

        if config_data[0] == "parts_config":
            self.parts_config = config_data[1]

        if config_data[0] == "material_config":
            self.additional_materials.append(config_data)


    def _get_config_data(self, file):
        with open(file, 'r') as contents:
            config = yaml.safe_load(contents)
        file_type = config["file_type"]
        del config["file_type"]
        return file_type, config


    def load_configs(self, case_directory = "."):
        '''Walk through case directory and load config files'''
        for root, _, files in os.walk(case_directory):
            for file in files:
                if file.endswith(".yml"):
                    path = os.path.join(root, file)
                    config_data = self._get_config_data(path)
                    self._sort_config_data(config_data)
