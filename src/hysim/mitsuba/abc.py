from __future__ import annotations

from typing import Any, TypeVar, Generic, ClassVar, Union, Annotated
from pydantic import (
    BaseModel,
    field_validator,
    ConfigDict,
    Field,
    model_validator,
    TypeAdapter,
    ValidatorFunctionWrapHandler,
)

import hysim.util.mitsuba_types as mit

# Type aliases
Transform = mit.Transform
Vector = mit.Vector


class MitsubaObject(BaseModel):
    """Abstract base class for Mitsuba objects"""

    _subclasses: ClassVar[dict[str, type[MitsubaObject]]] = {}
    _abstract_subclasses: ClassVar[set[type[MitsubaObject]]] = set()
    _type_adapter: ClassVar[TypeAdapter] = None

    def __new__(cls, *args, **kwargs):
        if cls in MitsubaObject._abstract_subclasses:
            raise TypeError(
                f"{cls.__name__} is an abstract class and cannot be instantiated directly."
            )
        return super().__new__(cls)

    # https://github.com/pydantic/pydantic/issues/7366
    @model_validator(mode="wrap")
    @classmethod
    def _parse_into_subclass(
        cls, v: Any, handler: ValidatorFunctionWrapHandler
    ) -> MitsubaObject:
        if cls in MitsubaObject._abstract_subclasses:
            if MitsubaObject._type_adapter is None:
                MitsubaObject._type_adapter = TypeAdapter(
                    Annotated[
                        Union[tuple(MitsubaObject._subclasses.values())],
                        Field(discriminator="type"),
                    ]
                )
            return MitsubaObject._type_adapter.validate_python(v)
        return handler(v)

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        key = cls.model_fields.get("type")
        if key is None:  # (is an "abstract" class)
            MitsubaObject._abstract_subclasses.add(cls)
        else:
            MitsubaObject._subclasses[key.default] = cls

    @field_validator("to_world", "direction", mode="plain", check_fields=False)
    @classmethod
    def _ignore_transforms(cls, v):
        return v

    def asdict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True, serialize_as_any=True)


# Named mitsuba objects are: Sensors, Emitters, BSDFs, Shapes and Spectra types.
_NamedMitsubaObject = TypeVar("_NamedMitsubaObject", bound=MitsubaObject)


class NamedObjectsMixin(BaseModel, Generic[_NamedMitsubaObject]):
    """Mixin class for Mitsuba objects that have named objects
    to easily apply them to the object in question"""

    model_config = ConfigDict(extra="allow")

    # Need to add better support if the name is already used,
    def _add_item(self, name: str, item: _NamedMitsubaObject):
        if name is None:
            raise AttributeError(f'"name" cannot be None')
        if not isinstance(name, str):
            raise TypeError(f'"name" must be a string, not {type(name)}')
        if not isinstance(item, MitsubaObject):
            raise TypeError(f'"item" must be a MitsubaObject, not {type(item)}')
        setattr(self, name, item)
