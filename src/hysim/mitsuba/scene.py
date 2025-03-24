from hysim.mitsuba.abc import *
from hysim.mitsuba.abc import _iterate_named_objects
from hysim.mitsuba.emitters import Emitter
from hysim.mitsuba.integrators import Integrator
from hysim.mitsuba.sensors import Sensor
from hysim.mitsuba.shapes import Shape


class Scene(MitsubaObject):
    _integrator: Integrator
    _sensors: List[Sensor] = []
    _emitters: List[Emitter] = []
    _shapes: List[Shape] = []

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
        return self._integrator

    def set_integrator(self, integrator: Integrator):
        self._integrator = integrator

    def add_sensor(self, sensor: Sensor):
        self._sensors.append(sensor)

    def add_shape(self, shape: Shape):
        self._shapes.append(shape)

    def add_emitter(self, emitter: Emitter):
        self._emitters.append(emitter)
        pass
