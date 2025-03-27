"""Shapes adapted from:
https://mitsuba.readthedocs.io/en/stable/src/generated/plugins_shapes.html"""

from hysim.mitsuba.abc import *
from hysim.mitsuba.bsdfs import BSDF


class Shape(NamedMitsubaObject):
    """Abstract base class for Mitsuba shape objects"""

    to_world: Transform
    pass


class PlyMesh(Shape):
    filename: str
    material: BSDF
    # face_normals: bool = False
    # flip_normals: bool = False
    # flip_tex_coords: bool = False

    @property
    def asdict(self) -> MDict:
        d = {
            "type": "ply",
            "filename": self.filename,
            "to_world": self.to_world,
        }
        if self.material.name:
            d[self.material.name] = self.material.asdict
        else:
            d["material"] = self.material.asdict
        return d
