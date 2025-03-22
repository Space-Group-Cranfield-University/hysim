from hysim.mitsuba.abc import *
from hysim.mitsuba.bsdfs import BSDF


class Shape(NamedMitsubaObject):
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
        return {
            "type": "ply",
            "filename": self.filename,
            "to_world": self.to_world,
            "material": self.material.asdict,
        }
