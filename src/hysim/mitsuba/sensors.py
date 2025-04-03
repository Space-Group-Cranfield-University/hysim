"""Sensors adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_sensors.html"""
from typing import Union, Literal

from hysim.mitsuba.abc import MitsubaObject, Transform
from hysim.mitsuba.films import Films
from hysim.mitsuba.samplers import Samplers


class Sensor(MitsubaObject):
    """Abstract base class for Mitsuba sensor objects"""

    near_clip: float = 0.01
    far_clip: float = 1e20
    to_world: Transform
    film: Films
    fov: float
    fov_axis: str = "x"
    sampler: Samplers


class ThinLensCamera(Sensor):
    type: Literal["thinlens"] = "thinlens"
    focal_distance: float
    focus_distance: float
    aperture_radius: float


class PerspectiveCamera(Sensor):
    type: Literal["perspective"] = "perspective"


Sensors = Union[ThinLensCamera, PerspectiveCamera]
