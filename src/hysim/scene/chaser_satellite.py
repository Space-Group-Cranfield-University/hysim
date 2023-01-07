"""Chaser Module

This module contains classes representing the chaser spacecraft and
the hyperspectral sensor.
"""
import mitsuba as mi
from abc import ABC, abstractmethod
from dataclasses import dataclass
from hysim.scene import spectra


@dataclass
class SpectralFilm:
    """Represents spectral film in sensor

    Attributes
    ----------
    spectrum : HyperspectralFilmResponse
        Film spectrum object
    width : int, optional[768]
        Film width in pixels
    height : int, optional [576]
        Film height in pixels
    component_format : str, optional["float32"]
        Format of film spectrum values
    film_dict : dict, optional[None]
        Film object in dict form, initialized as None

    Methods
    -------
    build_dict
        Creates film dict from template

    """

    spectrum: spectra.Spectrum
    width: int = 768
    height: int = 576
    component_format: str = "float32"
    film_dict: dict = None

    def build_dict(self):
        """Creates the spectral film dictionary using object attributes"""
        self.film_dict = {
            "type": "specfilm",
            "width": self.width,
            "height": self.height,
            "component_format": self.component_format,
        }
        self.film_dict.update(self.spectrum.build_dict())


@dataclass
class Camera(ABC):
    """Class

    Attributes
    ----------
    near_clip : float, optional[0.01]
        Minimum render distance [m]
    far_clip : float, optional[1e20]
        Maximum render distance [m]

    Methods
    -------
    build_dict
        Abstract method for creating a dict describing camera
    """

    near_clip: float = 0.01
    far_clip: float = 1e20

    @abstractmethod
    def build_dict(self):
        """Abstract builder method for camera types

        For each camera type the object data needs to be turned
        into a dictionary with a specific structure that mitsuba
        will recognise. Each inherited type must implement a
        mitsuba recognisable camera type.
        """


@dataclass
class ThinLenseCamera(Camera):
    """Represents Mitsuba thin lense camera

    Attributes
    ----------
    field_of_view : float
        Camera field of view
    fov_axis : str optional["x"]
        Camera axis along which field of view is measured
    aperture_radius : float
        Lens aperture radius
    focus_distance : float
        Focus distance of the camera
    camera_dict : dict
        Dictionary representing camera

    Methods
    -------
    build_dict
        Creates dictionary that represents camera from template

    """

    field_of_view: float = None
    fov_axis: str = "x"
    aperture_radius: float = None
    focus_distance: float = None
    camera_dict: dict = None

    def build_dict(self):
        """Creates the Thin Lense dictionary using object attributes"""
        self.camera_dict = {
            "type": "thinlens",
            "aperture_radius": self.aperture_radius,
            "focus_distance": self.focus_distance,
            "fov": self.field_of_view,
            "fov_axis": self.fov_axis,
            "near_clip": self.near_clip,
            "far_clip": self.far_clip,
            "film": {},
            "sampler": {},
        }


@dataclass
class PerspectiveCamera(Camera):
    """Represents Mitsuba perspective camera

    Attributes
    ----------
    field_of_view : float
        Camera field of view
    fov_axis : str optional["x"]
        Camera axis along which field of view is measured
    camera_dict : dict
        Dictionary representing camera

    Methods
    -------
    build_dict
        Creates dictionary that represents camera from template

    """

    field_of_view: float = None
    fov_axis: str = "x"
    camera_dict: dict = None

    def build_dict(self):
        """Creates the Thin Lense dictionary using object attributes"""
        self.camera_dict = {
            "type": "perspective",
            "fov": self.field_of_view,
            "fov_axis": self.fov_axis,
            "near_clip": self.near_clip,
            "far_clip": self.far_clip,
            "film": {},
            "sampler": {},
        }


@dataclass
class SpectralSensor:
    """Represents a spectral sensor consisting of a film and camera

    Represents a spectral type sensor consisting of the film and camera.
    Mitsuba requires that the sampler is also included in the final
    dictionary representing this object in the scene.

    Attributes
    ----------
    film : SpectralFilm
        Film object
    camera : Camera
        Camera object
    sampler : dict
        Sampler dictionary defining sampler type and number of samples
    sensor_dict : dict
        Dictionary describing sensor object

    Methods
    -------
    build_dict
        Builds the dictionary representing a spectral sensor
    """

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


class Chaser:
    """Represents Chaser spacecraft

    Chaser spacecraft consists of a sensor, a defined position and
    defined attitude.

    Attributes
    ----------
    sensor : SpectralSensor
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
            .rotate(axis=[1, 0, 0], angle=self.attitude[0])
            .rotate(axis=[0, 1, 0], angle=self.attitude[1])
            .rotate(axis=[0, 0, 1], angle=self.attitude[2])
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
