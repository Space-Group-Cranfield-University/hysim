"""Space environment scene objects"""
import mitsuba as mi


class Sun:
    """Sun object in scene environment"""

    def __init__(self, irradiance_spectrum) -> None:
        self.sun_dict = None
        self.sun_position = None
        self.irradiance_spectrum = irradiance_spectrum

    def position_sun_in_simple_3d(self, direction):
        """Position sun using simple cartesian direction vector"""
        self.sun_position = direction

    def build_dict(self):
        self.sun_dict = {
            "sun_emitter": {
                "type": "directional",
                "direction": self.sun_position,  # Sun pointing to +Y
                "irradiance": self.irradiance_spectrum.build_dict(),
            }
        }


class Earth:

    # radius = 6371000  # Earth Radius [m]

    """Earth object in scene environment"""
    def __init__(self):
        self.mesh_path = ""
        self.earth_image_path = ""
        self.soil_spectrum_path = ""
        self.ocean_spectrum_path = ""
        self.position = []

    def build_dict(self):
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
