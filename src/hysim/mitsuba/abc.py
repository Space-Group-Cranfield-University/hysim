from typing import TypeVar, Literal, Annotated, Generic, Any
import mitsuba as mi
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Type aliases
if mi.variant() is None:
    try:
        from mitsuba.scalar_rgb import ScalarTransform4f as Transform, Vector3f as Vector
    except ImportError:
        import importlib

        _mitsuba = importlib.import_module("mitsuba." + mi.variants()[0])
        Transform = _mitsuba.ScalarTransform4f
        Vector = _mitsuba.Vector3f
else:
    Transform = mi.ScalarTransform4f
    Vector = mi.Vector3f

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
    __pydantic_extra__: dict[str, Annotated[_NamedMitsubaObject, Discriminator]] = {}

    # Need to better support if the name is already used,
    def _add_item(self, name: str, item: _NamedMitsubaObject):
        if name is None:
            raise AttributeError(f"\"name\" cannot be None")
        if not isinstance(name, str):
            raise TypeError(f"\"name\" must be a string, not {type(name)}")
        if not isinstance(item, MitsubaObject):
            raise TypeError(f"\"item\" must be a MitsubaObject, not {type(item)}")
        setattr(self, name, item)
