""" Classes to hold sensor parameters and represent them as a dict"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from hyperspacesim.sim.spectra import FilmSensitivitySpectrum


# ---------- FILM ---------- #
@dataclass
class SpectralFilm:
    """Holds data on spectral film"""

    spectrum: FilmSensitivitySpectrum
    width: int = 768
    height: int = 576
    component_format: str = "float32"
    film_dict: dict = None

    def build_dict(self):
        """Builts the film dict using attributes and adds on spectrum dicts"""
        self.film_dict = {
            "type": "specfilm",
            "width": self.width,
            "height": self.height,
            "component_format": self.component_format,
        }
        self.film_dict.update(self.spectrum.build_dict())


# ---------- CAMERA ---------- #
@dataclass
class Camera(ABC):
    """Abstract class to based"""

    near_clip: float = 0.01
    far_clip: float = 1e8

    @abstractmethod
    def build_dict(self):
        """Abstract method that builds dict from camera parameters.
        Implement in subclasses"""


@dataclass
class ThinLenseCamera(Camera):
    """Holds parameters for thin lense cameras"""

    field_of_view: float = None
    fov_axis: str = "x"
    aperture_radius: float = None
    focus_distance: float = None
    camera_dict: dict = None

    def build_dict(self):
        """Builds dict from parameters"""
        self.camera_dict = {
            "type": "thinlens",
            "aperture_radius": self.aperture_radius,
            "focus_distance": self.focus_distance,
            "fov": self.field_of_view,
            "fov_axis": self.fov_axis,
            "near_clip": self.near_clip,
            "far_clip": self.far_clip,
            "film": {},
            "sampler": {}
        }


# ---------- SENSOR ---------- #
@dataclass
class SpectralSensor:
    """Holds spectral film and camera data that makes up a sensor"""

    film: SpectralFilm
    camera: Camera
    sampler: dict
    sensor_dict: dict = None

    def build_dict(self):
        """Builds dictionary for spectral sensor out of camera, film and
        sampler"""
        # Build camera and film dicts inside objects
        self.camera.build_dict()
        self.film.build_dict()

        # Add to sensor dict
        self.sensor_dict = {"sensor": None}
        self.sensor_dict["sensor"] = self.camera.camera_dict
        self.sensor_dict["sensor"]["film"].update(self.film.film_dict)
        self.sensor_dict["sensor"].update(self.sampler)
