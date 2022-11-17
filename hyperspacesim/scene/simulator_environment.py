"""Space environment parameters"""
from dataclasses import dataclass


@dataclass
class Sun:
    """Sun object in scene environment"""
    sun_dict: dict = None

    def __init__(self, irradiance_spectrum):
        self.irradiance_spectrum = irradiance_spectrum
        self.sun_position = None

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
