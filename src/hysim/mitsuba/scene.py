from typing import Union, Literal, Annotated

from hysim.mitsuba.abc import MitsubaObject, NamedObjectsMixin, Discriminator
from hysim.mitsuba.emitters import Emitters
from hysim.mitsuba.integrators import Integrators
from hysim.mitsuba.sensors import Sensors
from hysim.mitsuba.shapes import Shapes


class Scene(MitsubaObject, NamedObjectsMixin[Union[Sensors, Shapes, Emitters]]):
    """Mitsuba scene object
    Use with mitsuba.load_dict() to generate a Mitsuba scene
    """

    type: Literal["scene"] = "scene"
    integrator: Integrators

    __pydantic_extra__: dict[str, Annotated[Union[Sensors, Shapes, Emitters], Discriminator]]

    def add_sensor(self, name: str, sensor: Sensors):
        """Add a sensor to the scene"""
        self._add_item(name, sensor)

    def add_shape(self, name: str, shape: Shapes):
        """Add a shape to the scene"""
        self._add_item(name, shape)

    def add_emitter(self, name: str, emitter: Emitters):
        """Add an emitter to the scene"""
        self._add_item(name, emitter)
