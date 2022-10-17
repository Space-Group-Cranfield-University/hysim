# Spectral Sensors
'''
doc string
'''

import numpy as np
import hyperspacesim.data as data

class SpectralSensor:
    '''
    Spectral Sensor Class.
    '''
    def __init__(
            self,
            spectrum_file,
            number_of_bands,
            film_resolution=(768, 576),
            component_format="float32",
        ):
        self.film_resolution = film_resolution
        self.component_format = component_format
        self.spectral_response = SpectralBands(number_of_bands, spectrum_file)


class PerspectiveCamera(SpectralSensor):
    def __init__(
            self,
            spectrum_file,
            number_of_bands,
            field_of_view,
            film_resolution=(768, 576),
            component_format="float16",
            focal_length = "50mm",
            fov_axis = "x",
            near_clip = 0.01,
            far_clip = 10000
        ):

        super().__init__(
            spectrum_file,
            number_of_bands,
            film_resolution,
            component_format,
        )

        self.field_of_view = field_of_view
        self.focal_length = focal_length
        self.fov_axis = fov_axis
        self.near_clip = near_clip
        self.far_clip = far_clip


class ThinLenseCamera(PerspectiveCamera):
    def __init__(
            self,
            spectrum_file,
            number_of_bands,
            field_of_view,
            aperture_radius,
            film_resolution=(768, 576),
            component_format="float16",
            focal_length = "50mm",
            fov_axis = "x",
            near_clip = 0.01,
            far_clip = 10000,
            focus_distance = 0.0
        ):

        super().__init__()

        self.aperture_radius = aperture_radius
        self.focus_distance = focus_distance
