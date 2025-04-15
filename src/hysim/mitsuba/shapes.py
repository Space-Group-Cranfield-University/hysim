"""Shapes adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_shapes.html"""

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


Shapes = PlyMesh  # Union[PlyMesh]  # create_type_alias(Shape)
