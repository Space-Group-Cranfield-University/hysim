'''Space environment parameters'''

from hyperspacesim.sim import spectra

class Sun:
    '''Sun object in scene environment'''
    def __init__(self, irradiance_spectrum):
        self.irradiance_spectrum = irradiance_spectrum
        self.sun_position = None

    def position_sun_in_simple_3d(self, direction):
        '''Position sun using simple cartesian direction vector'''
        self.sun_position = direction
    
    def build_dict(self):
        return {
        "sun_emitter": {
            "type": "directional",
            "direction": self.sun_position, # Sun pointing to +Y in sun-sync orbit
            "irradiance": self.irradiance_spectrum.build_dict()
        }}
    
