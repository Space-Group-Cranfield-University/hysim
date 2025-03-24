"""Adapted from: https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_sensors.html"""
from hysim.mitsuba.abc import *
from hysim.mitsuba.films import Film
from hysim.mitsuba.samplers import Sampler


class Sensor(NamedMitsubaObject):
    near_clip: float = 0.01
    far_clip: float = 1e20
    to_world: Transform
    film: Film
    fov: float
    fov_axis: str = "x"
    sampler: Sampler

    @property
    @abstractmethod
    def asdict(self) -> MDict:
        """Builds the sensor dictionary"""
        return {
            "type": None,
            "far_clip": self.far_clip,
            "near_clip": self.near_clip,
            "film": self.film.asdict,
            "fov": self.fov,
            "fov_axis": self.fov_axis,
            "sampler": self.sampler.asdict,
            "to_world": self.to_world
        }


class ThinLensCamera(Sensor):
    focal_distance: float
    focus_distance: float
    aperture_radius: float

    @property
    def asdict(self) -> MDict:
        d = super().asdict
        d["type"] = "thinlens"
        d["focal_distance"] = self.focal_distance
        d["focus_distance"] = self.focus_distance
        d["aperture_radius"] = self.aperture_radius
        return d


class PerspectiveCamera(Sensor):
    @property
    def asdict(self) -> MDict:
        d = super().asdict
        d["type"] = "perspective"
        return d
