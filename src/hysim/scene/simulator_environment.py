"""Space Environment Module

Contains classes to desribe objects in the Space Environment such as the Earth
and Sun. The Earth is represented at scale and the Sun is represented by a
directional light source.
"""
import mitsuba as mi

import hysim.scene.spectra as spectra


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
                "earth_surface": {
                    "type": "blendbsdf",
                    "weight": {
                        "type": "bitmap",
                        "filename": self.earth_image_path,
                        "wrap_mode": "clamp",
                    },
                    "ocean": {
                        "type": "diffuse",
                        "reflectance": {
                            "type": "spectrum",
                            "filename": self.ocean_spectrum_path,
                        },
                    },
                    "soil": {
                        "type": "diffuse",
                        "reflectance": {
                            "type": "spectrum",
                            "filename": self.soil_spectrum_path,
                        },
                    },
                },
            }
        }
