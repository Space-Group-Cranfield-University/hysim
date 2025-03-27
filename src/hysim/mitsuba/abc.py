import typing_extensions
from abc import ABC, abstractmethod
from typing import Any, Optional, Union, Iterable
import mitsuba as mi

# Type aliases
if mi.variant() is None:
    Transform = list[list[float]]
    Vector = list[float]
else:
    # TODO: potentially replace with https://mitsuba.readthedocs.io/en/stable/src/key_topics/scene_format.html#transformations
    Transform = mi.ScalarTransform4f
    Vector = mi.Vector3f

MDict = dict[str, Any]


class MitsubaObject(ABC):
    """Abstract base class for Mitsuba objects"""

    # TODO: add type:str field to allow for more accurate type checking when using pydantic
    # and Union (pydantic will check the type field which will be a literal on concrete implementations)
    # e.g type: Literal[str] = "diffuse" for the DiffuseMaterial

    # mitsuba_dict: MDict

    @property
    @abstractmethod
    def asdict(self) -> MDict:
        """Returns the object as a dict for use with Mitsuba"""
        raise NotImplementedError


class NamedMitsubaObject(MitsubaObject):
    name: Optional[str] = None


def _iterate_named_objects(
    d: MDict, objects: Iterable[NamedMitsubaObject], default_prefix: str
):
    """
    Iterates over a collection of potential named mitsuba objects and adds them to the dictionary
    Parameters
    ----------
    d : MDict
        The dictionary to add the objects to.
    objects : Iterable[NamedMitsubaObject]
        The collection of objects to iterate.
    default_prefix : str
        The default prefix to use for the object if it does not have a name.
    """
    for i, obj in enumerate(objects):
        if obj.name:
            d[obj.name] = obj.asdict
        else:
            d[f"{default_prefix}_{i}"] = obj.asdict


def _get_subclasses(cls: type) -> typing_extensions.TypeAlias:
    return Union[tuple(cls.__subclasses__())]


# class IPositionedMitsubaObject(Protocol):
#     to_world: mi.ScalarTransform4f


# class HasFileName(Protocol):
#     filename: str


# TODO: move all abstract classes to abc.py
# Also could implement a factory pattern for creating objects

# Alternatively instead of using classes, could have the user/builder set the
# type of object themselves e.g.
# sensor = Sensor()
# sensor.type = "perspective"
# sensor.fov = 45
# sensor.film = Film()
