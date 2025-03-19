from typing import Set
from hysim.mitsuba.abc import *
from hysim.mitsuba.integrators import Integrator
from hysim.mitsuba.sensors import Sensor
from hysim.mitsuba.shapes import Shape


class Scene(MitsubaObject):
    _integrator: Integrator
    _sensors: Set[Sensor]
    #emitters: Set[Emitter]
    _shapes: Set[Shape]

    @property
    def asdict(self) -> MDict:
        d = {
            "type": "scene",
            "integrator": self.integrator.asdict,
        }
        #for i, sen

        return d

    @property
    def integrator(self) -> Integrator:
        return self._integrator

    def set_integrator(self, integrator: Integrator):
        self._integrator = integrator

    def add_sensor(self, sensor: Sensor):
        self._sensors.add(sensor)

    def add_shape(self, shape: Shape):
        self._shapes.add(shape)
