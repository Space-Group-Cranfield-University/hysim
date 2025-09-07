from typing import Union, Literal

from .abc import MitsubaObject, NamedObjectsMixin
from .emitters import Emitter as _Emitter
from .integrators import Integrator as _Integrator
from .sensors import Sensor as _Sensor
from .shapes import Shape as _Shape


class Scene(MitsubaObject, NamedObjectsMixin[Union[_Sensor, _Shape, _Emitter]]):
    """Mitsuba scene object
    Use with mitsuba.load_dict() to generate a Mitsuba scene
    """

    type: Literal["scene"] = "scene"
    integrator: _Integrator

    __pydantic_extra__: dict[str, Union[_Sensor, _Shape, _Emitter]] = {}

    def add_sensor(self, name: str, sensor: _Sensor):
        """Add a sensor to the scene"""
        self._add_item(name, sensor)

    def add_shape(self, name: str, shape: _Shape):
        """Add a shape to the scene"""
        self._add_item(name, shape)

    def add_emitter(self, name: str, emitter: _Emitter):
        """Add an emitter to the scene"""
        self._add_item(name, emitter)

