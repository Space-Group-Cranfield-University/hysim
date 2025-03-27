from hysim.mitsuba.abc import *
from hysim.mitsuba.abc import _iterate_named_objects
from hysim.mitsuba.emitters import Emitter
from hysim.mitsuba.integrators import Integrator
from hysim.mitsuba.sensors import Sensor
from hysim.mitsuba.shapes import Shape


class Scene(MitsubaObject):
    """Mitsuba scene object
    Use with mitsuba.load_dict() to generate a Mitsuba scene
    """

    _integrator: Integrator
    _sensors: list[Sensor] = []
    _emitters: list[Emitter] = []
    _shapes: list[Shape] = []

    @property
    def asdict(self) -> MDict:
        d = {
            "type": "scene",
            "integrator": self.integrator.asdict,
        }
        _iterate_named_objects(d, self._sensors, "sensor")
        _iterate_named_objects(d, self._emitters, "emitter")
        _iterate_named_objects(d, self._shapes, "shape")
        return d

    @property
    def integrator(self) -> Integrator:
        """Get the integrator for the scene
        Returns
        -------
        Integrator
            The integrator for the scene
        """
        return self._integrator

    def set_integrator(self, integrator: Integrator):
        """Set the integrator for the scene"""
        self._integrator = integrator

    def add_sensor(self, sensor: Sensor):
        """Add a sensor to the scene"""
        self._sensors.append(sensor)

    def add_shape(self, shape: Shape):
        """Add a shape to the scene"""
        self._shapes.append(shape)

    def add_emitter(self, emitter: Emitter):
        """Add an emitter to the scene"""
        self._emitters.append(emitter)
