"""Shapes adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_shapes.html"""
from typing import Optional

from pydantic import model_serializer
from pydantic_core.core_schema import SerializerFunctionWrapHandler

from hysim.mitsuba.abc import *
from hysim.mitsuba.bsdfs import BSDFs


class Shape(MitsubaObject):
    """Abstract base class for Mitsuba shape objects"""

    to_world: Transform
    pass


class PlyMesh(Shape):
    type: Literal["ply"] = "ply"
    filename: str
    material: BSDFs
    # face_normals: bool = False
    # flip_normals: bool = False
    # flip_tex_coords: bool = False
    material_name : Optional[str] = Field(exclude=True, default="material")

    # TODO: this is also on bsdfs. Create a mixin for this or a custom serializer?
    @model_serializer(mode="wrap")
    def material_serializer(self, nxt: SerializerFunctionWrapHandler, info):
        partial_result = nxt(self, info)
        partial_result[self.material_name] = partial_result.pop("material")
        return partial_result

Shapes = PlyMesh # Union[PlyMesh]  # create_type_alias(Shape)