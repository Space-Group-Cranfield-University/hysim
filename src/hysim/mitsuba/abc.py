import typing_extensions
from abc import ABC, abstractmethod
from typing import List, Any, Dict, Optional, Union, Annotated
import mitsuba as mi

# Type aliases
if mi.variant() is None:
    Transform = List[List[float]]
    Vector = List[float]
else:
    Transform = mi.Transform4f
    Vector = mi.Vector3f

MDict = Dict[str, Any]


class MitsubaObject(ABC):
    """Abstract base class for Mitsuba objects"""

    # mitsuba_dict: MDict

    @property
    @abstractmethod
    def asdict(self) -> MDict:
        """Returns the object as a dict for use with Mitsuba"""
        raise NotImplementedError


class NamedMitsubaObject(MitsubaObject):
    name: Optional[str] = None


def create_type_alias(cls: type) -> typing_extensions.TypeAlias:
    return Annotated[
        Union[tuple(cls.__subclasses__())], "Type alias for " + cls.__name__ + "s"
    ]


# class IPositionedMitsubaObject():
#     to_world: mi.ScalarTransform4f


# class HasFileName():
#     filename: str


# TODO: move all abstract classes to abc.py
# Also could implement a factory pattern for creating objects

# Alternatively instead of using classes, could have the user/builder set the
# type of object themselves e.g.
# sensor = Sensor()
# sensor.type = "perspective"
# sensor.fov = 45
# sensor.film = Film()
