"""Space Environment Module

Contains classes to desribe objects in the Space Environment such as the Earth
and Sun. The Earth is represented at scale and the Sun is represented by a
directional light source.
"""
import mitsuba as mi
import numpy as np

import hysim.scene.spectra as spectra
from hysim.data import data_handling as dh


class Sun:
    """Sun object in scene environment

    Attributes
    ----------
    sun_dict : dict
        Dictionary representing Sun in scene
    sun_position : list
        Sun position in ECI
    Irradiance spectrum : spectra.IrradianceSpectrum
        Spectrum object representing the sunlight irradiance

    Methods
    -------
    position_sun_in_simple_3d(direction)
        Sets direction of the sun with direction vector

    """

    def __init__(self, irradiance_spectrum: spectra.IrradianceSpectrum):
        """Initializer

        Parameters
        ----------
        irradiance_spectrum : spectra.IrradianceSpectrum
            Sunlight spectrum
        """
        self.sun_dict = None
        self.sun_position = None
        self.irradiance_spectrum = irradiance_spectrum

    def position_sun_in_simple_3d(self, direction: list):
        """Set sun direction vector

        Parameters
        ----------
        direction : list
            Sunlight direction vector relative to target
        """
        self.sun_position = direction

    def build_dict(self):
        """Constucts dictionary for Sun object in Mitsuba scene"""
        self.sun_dict = {
            "sun_emitter": {
                "type": "directional",
                "direction": self.sun_position,  # Sun pointing to +Y
                "irradiance": self.irradiance_spectrum.build_dict(),
            }
        }


class Earth:
    """Earth object in scene

    Attributes
    ----------
    mesh_path : str
        Path to the mesh used for Earth
    earth_image_path : str
        Bitmap image of earth land/water
    soil_spectrum_path: str
        Path to file containing soil spectrum
    ocean_spectrum_path : str
        Path to file containing ocean water spectrum
    position : list
        Position of earth in cartesian reference frame [x, y, z]

    Methods
    -------
    build_dict
        Builds dictionary describing Earth in scene

    """

    def __init__(self):
        """Initializer"""
        self.mesh_path = ""
        self.earth_image_path = ""
        self.soil_spectrum_path = ""
        self.ocean_spectrum_path = ""
        self.position = []

    def build_dict(self):
        """Consutucts dictionary for Earth object in mitsuba scene"""
        self.earth_dict = {
            "earth": {
                "type": "ply",
                "filename": self.mesh_path,
                "to_world": mi.ScalarTransform4f.translate(self.position),
                "ocean_surface": {
                    "type": "diffuse",
                    "reflectance": {
                        "type": "spectrum",
                        "filename": self.ocean_spectrum_path,
                    },
                },
            }
        }

        # self.earth_dict = {
        #     "earth": {
        #         "type": "ply",
        #         "filename": self.mesh_path,
        #         "to_world": mi.ScalarTransform4f.translate(self.position),
        #         "earth_surface": {
        #             "type": "blendbsdf",
        #             "weight": {
        #                 "type": "bitmap",
        #                 "filename": self.earth_image_path,
        #                 "wrap_mode": "clamp",
        #             },
        #             "ocean": {
        #                 "type": "diffuse",
        #                 "reflectance": {
        #                     "type": "spectrum",
        #                     "filename": self.ocean_spectrum_path,
        #                 },
        #             },
        #             "soil": {
        #                 "type": "diffuse",
        #                 "reflectance": {
        #                     "type": "spectrum",
        #                     "filename": self.soil_spectrum_path,
        #                 },
        #             },
        #         },
        #     }
        # }


"""Chaser Module

This module contains classes representing the chaser spacecraft and
the hyperspectral sensor.
"""
class Chaser:
    """Represents Chaser spacecraft

    Chaser spacecraft consists of a sensor, a defined position and
    defined attitude.

    Attributes
    ----------
    sensor : hysim.scene.sensors.SpectralSensor
        Spectral sensor object
    position : list
        Position coordinates [x, y, z] [m]
    attitude : list
        Attitude defined by euler angles in LVLH frame [x-axis, y-axis, z-axis]
    chaser_dict : dict

    Methods
    -------
    __return_mitsuba_transform
        Returns mitsuba scalar transform
    build_dict
        Builds dict describing chaser
    """

    def __init__(self, sensor):
        self.sensor = sensor
        self.position = []
        self.attitude = []
        self.chaser_dict = {}

    def set_lookat_attitude(self):
        """Set attitude to lookat mode"""
        self.attitude = "lookat"

    def __return_mitsuba_transform(self):
        """Return mitsuba ScalarTransform4f

        Returns mitsuba transform using position and attitude
        attributes.

        Returns
        -------
        mi.ScalarTransform4f
            Scalar transform to orient object in scene
        """
        return (
            mi.ScalarTransform4f.translate(self.position)
            .rotate(axis=[1, 0, 0], angle=np.rad2deg(self.attitude[0]))
            .rotate(axis=[0, 1, 0], angle=np.rad2deg(self.attitude[1]))
            .rotate(axis=[0, 0, 1], angle=np.rad2deg(self.attitude[2]))
        )

    def build_dict(self):
        """Builds the dictionary describing chaser sensor and
        location/attitude

        Builds sensor dictionary and adds location of chaser to define
        the chaser dict for loading into mitsuba. If the attitude is
        defined is "lookat" then a lookat transform is used. This
        calculates the required attitude to look at the target. Else
        the attitude and position provided is applied by calculating a
        transform (see _return_mitsuba_tranform).
        """
        self.sensor.build_dict()
        self.chaser_dict.update(self.sensor.sensor_dict)

        if self.attitude == "lookat":
            self.chaser_dict["sensor"].update(
                {
                    "to_world": mi.ScalarTransform4f.look_at(
                        origin=self.position,
                        target=[0, 0, 0],
                        up=[0, 0, -1],  # Assumed +z is nadir
                    )
                }
            )
        else:
            self.chaser_dict["sensor"].update(
                {"to_world": self.__return_mitsuba_transform()}
            )


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

"""Target Satellite Module

Module containing classes that manage the Target model in the scene
"""
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
            .rotate(axis=[1, 0, 0], angle=np.rad2deg(self.attitude[0]))
            .rotate(axis=[0, 1, 0], angle=np.rad2deg(self.attitude[1]))
            .rotate(axis=[0, 0, 1], angle=np.rad2deg(self.attitude[2]))
        )

    def build_dict(self):
        """Builds target dictionary"""
        self.target_dict = {}

        for part in self.target_model:
            self.target_dict.update({part.name: part.part_dict})
            self.target_dict[part.name]["to_world"] = self.__transform()

