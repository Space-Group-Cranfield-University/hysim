"""Sensors adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_sensors.html"""

from typing import Literal

from .abc import MitsubaObject, Transform
from .films import Film as _Film
from .samplers import Sampler as _Sampler


class Sensor(MitsubaObject):
    """Abstract base class for Mitsuba sensor objects"""

    near_clip: float = 0.01
    far_clip: float = 1e20
    to_world: Transform
    film: _Film
    fov: float
    fov_axis: str = "x"
    sampler: _Sampler


class ThinLensCamera(Sensor):
    type: Literal["thinlens"] = "thinlens"
    focal_distance: float
    focus_distance: float
    aperture_radius: float


class PerspectiveCamera(Sensor):
    type: Literal["perspective"] = "perspective"
