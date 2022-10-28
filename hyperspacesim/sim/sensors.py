''' Classes to hold sensor parameters and represent them as a dict'''

from abc import ABC, abstractmethod
from dataclasses import dataclass
from hyperspacesim.sim.spectra import FilmSensitivitySpectrum

### Film ###
@dataclass
class SpectralFilm:
    '''Holds data on spectral film'''
    spectrum: FilmSensitivitySpectrum
    resolution: tuple = (768, 576)
    component_format: str = "float32"

    def build_dict(self):
        '''Builts the film dict using attributes and adds on spectrum dicts'''
        film_dict = {"film":{
                "type": "specfilm",
                "width": self.resolution[0],
                "height": self.resolution[1],
                "component_format": self.component_format
                }}
        film_dict["film"].update(self.spectrum.build_dict())

        return film_dict

### Camera ###
@dataclass
class Camera(ABC):
    '''Abstract class to based'''
    near_clip: float = 0.01
    far_clip: float = 1e+8

    @abstractmethod
    def build_dict(self):
        '''Abstract method that builds dict from camera parameters.
        Implement in subclasses'''


@dataclass
class ThinLenseCamera(Camera):
    '''Holds parameters for thin lense cameras'''
    field_of_view: float = None
    fov_axis: str = "x"
    aperture_radius: float = None
    focus_distance: float = None

    def build_dict(self):
        '''Builds dict from parameters'''
        return {
            "type": "thinlense",
            "aperture_radius": self.aperture_radius,
            "focus_distance": self.focus_distance,
            "fov": self.field_of_view,
            "fov_axis": self.fov_axis,
            "near_clip": self.near_clip,
            "far_clip": self.far_clip
        }


### Spectral Sensor ###
@dataclass
class SpectralSensor:
    '''Holds spectral film and camera data that makes up a sensor'''
    film: SpectralFilm
    camera: Camera

    def build_dict(self):
        '''Builds dictionary for spectral sensor out of camera, film and sampler'''
        sensor_dict = self.camera.build_dict()
        sensor_dict.update(self.film.build_dict())

        return sensor_dict


# @dataclass
# class PerspectiveCamera(Camera):
#     '''Holds parameters for perspective cameras'''
#     field_of_view: float = None
#     fov_axis: str = "x"

#     def build_dict(self):
#         '''Builds dict from parameters'''
#         return {
#             "type": "perspective",
#             "fov": self.field_of_view,
#             "fov_axis": self.fov_axis,
#             "near_clip": self.near_clip,
#             "far_clip": self.far_clip
#         }
