"""Space environment parameters"""


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