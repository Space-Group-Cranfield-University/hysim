"""Shapes adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_shapes.html"""

from typing import Literal

from .abc import MitsubaObject, Transform
from .bsdfs import BSDF


class Shape(MitsubaObject):
    """Abstract base class for Mitsuba shape objects"""

    to_world: Transform


class PlyMesh(Shape):
    type: Literal["ply"] = "ply"
    filename: str
    material: BSDF
    # face_normals: bool = False
    # flip_normals: bool = False
    # flip_tex_coords: bool = False


class Sphere(Shape):
    type: Literal["sphere"] = "sphere"
    radius: float = 1.0
    material: BSDF