from typing import TypeVar, Literal, Generic, Any
import hysim.util.mitsuba_types as mit
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Type aliases
Transform = mit.Transform
Vector = mit.Vector

Discriminator = Field(discriminator="type")


# Need to enforce abstract class without an abstract method implementation
class MitsubaObject(BaseModel):
    """Abstract base class for Mitsuba objects"""

    type: Literal[""]

    @field_validator("to_world", "direction", mode="plain", check_fields=False)
    @classmethod
    def ignore_mitsuba_types(cls, v):
        return v

    def asdict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)


# def _get_subclasses(cls: type) -> typing_extensions.TypeAlias:
#     return Union[tuple(cls.__subclasses__())]
# class _IPositioned(Protocol):
#     to_world:  Transform
# class HasFileName(Protocol):
#     filename: str

# TODO: move all abstract classes to abc.py

# Named mitsuba objects are: Sensors, Emitters, BSDFs, Shapes and Spectra types.
_NamedMitsubaObject = TypeVar("_NamedMitsubaObject", bound=MitsubaObject)


class NamedObjectsMixin(BaseModel, Generic[_NamedMitsubaObject]):
    """Mixin class for Mitsuba objects that have named objects
    to easily apply them to the object in question"""

    model_config = ConfigDict(extra="allow")

    # Need to better support if the name is already used,
    def _add_item(self, name: str, item: _NamedMitsubaObject):
        if name is None:
            raise AttributeError(f"\"name\" cannot be None")
        if not isinstance(name, str):
            raise TypeError(f"\"name\" must be a string, not {type(name)}")
        if not isinstance(item, MitsubaObject):
            raise TypeError(f"\"item\" must be a MitsubaObject, not {type(item)}")
        setattr(self, name, item)
