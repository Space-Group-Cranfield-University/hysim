"""Target Satellite Module

Module containing classes that manage the Target model in the scene
"""
import mitsuba as mi

from hysim.data import data_handling as dh


class PartBuilder:
    """Builder class to deal with target components

    For a given component of the target a mesh is assigned a material 
    so the component's dictionary can be built. This represents a single
    part of the target.

    Attributes
    ----------
    name : str
        Part name
    material : dict
        Material dict (contained within the part dict)
    mesh_file : str
        Path to mesh file
    part_dict
        Dictionary defining the part

    Methods
    -------
    set_database_material(material_name)
        Retrieves a material dict from the database
    set_user_material(material_dict)
        Assigns material dict passed by user to object
    build_dict
        Builds dictionary for part
    """

    def __init__(self, name):
        self.name = name
        self.material = {}
        self.mesh_file = ""
        self.part_dict = {}

    def set_database_material(self, material_name: str):
        """Get material from database and assign to material

        Parameters
        ----------
        material_name : str
            Name of the material in the database
        """
        material_dict = dh.get_material_from_database(material_name)
        self.material = material_dict

    def set_user_material(self, material_dict):
        """Set material from user defined file

        Parameters
        ----------
        material_dict : dict
            User defined dictionary passed to part directly
        """
        self.material = material_dict

    def build_dict(self):
        """Builds part dictionary"""
        part_dict = {
            "type": "ply",
            "filename": self.mesh_file,
            "to_world": None,
            self.name + "_material": self.material,
        }
        self.part_dict = part_dict


class Target:
    """Class that holds meshes and coordinates of model to represent target.

    Attributes
    ----------
    target_model : list[PartBuilder]
        List of parts in Target model
    position : list
        Coordinates of target in LVLH [x,y,z] (Default is 0,0,0)
    attitude : list
        Attitude in angles around x-axis, y-axis and z-axis
    target_dict : dict
        Dictionary defining target parameters


    Methods
    -------
    add_part(part)
        Appends list of parts (target_model) with new part
    remove_part(part)
        Removes existing part from target_model
    __transform
        Mitsuba transform to define location in scene
    build_dict
        Constructs Target dictionary
    """

    def __init__(self):
        """Initializer"""
        self.target_model = []
        self.position = []
        self.attitude = []
        self.target_dict = None

    def add_part(self, part: PartBuilder):
        """Appends target_model with newly constructed part

        Parameters
        ----------
        part : PartBuilder
            New part to add
        """
        self.target_model.append(part)

    def remove_part(self, part: str):
        """Removes existing part from target_model

        Parameters
        ----------
        part : str
            Name of the part to remove
        """
        del self.target_model[part]

    # TODO: Refactor this and chaser function into positioning module
    def __transform(self):
        """Makes mitsuba transform to position mesh in scene

        Returns
        -------
        mi.ScalarTransform4f
            Target transform
        """
        return (
            mi.ScalarTransform4f.translate(self.position)
            .rotate(axis=[1, 0, 0], angle=self.attitude[0])
            .rotate(axis=[0, 1, 0], angle=self.attitude[1])
            .rotate(axis=[0, 0, 1], angle=self.attitude[2])
        )

    def build_dict(self):
        """Builds target dictionary"""
        self.target_dict = {}

        for part in self.target_model:
            self.target_dict.update({part.name: part.part_dict})
            self.target_dict[part.name]["to_world"] = self.__transform()
