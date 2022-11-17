""" Classes for target object"""
import mitsuba as mi

from hyperspacesim.data import data_handling as dh


class PartBuilder:
    """Manages material assignment to mesh part"""

    def __init__(self, name):
        self.name = name
        self.material = {}
        self.mesh_file = ""
        self.part_dict = {}

    def set_database_material(self, material_name: str):
        """Get material from database and assign to material"""
        material_dict = dh.get_material_from_database(material_name)
        self.material = material_dict

    def set_user_material(self, material_dict):
        """Set material from user defined file"""
        self.material = material_dict

    def build_dict(self):
        part_dict = {
            "type": "ply",
            "filename": self.mesh_file,
            "to_world": None,
            self.name + "_material": self.material,
        }
        self.part_dict = part_dict


class Target:
    """Class that holds meshes and coordinates of model to represent target."""

    def __init__(self):
        self.target_model = []
        self.position = []
        self.attitude = []
        self.target_dict = None

    def set_position(self, position):
        pass

    def set_attitude(self, attitude):
        pass

    def add_part(self, part):
        self.target_model.append(part)

    def remove_part(self, part: str):
        del self.target_model[part]

    # TODO: Refactor this and chaser function into positioning module
    def __transform(self):
        return (
            mi.ScalarTransform4f.translate(self.position)
            .rotate(axis=[1, 0, 0], angle=self.attitude[0])
            .rotate(axis=[0, 1, 0], angle=self.attitude[1])
            .rotate(axis=[0, 0, 1], angle=self.attitude[2])
        )

    def build_dict(self):
        self.target_dict = {}

        for part in self.target_model:
            self.target_dict.update({part.name: part.part_dict})
            self.target_dict[part.name]["to_world"] = self.__transform()

