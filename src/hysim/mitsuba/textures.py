from typing import Literal
from .abc import MitsubaObject


class Texture(MitsubaObject):
    """Abstract base class for Mitsuba texture objects"""


class BitmapTexture(Texture):
    type: Literal["bitmap"] = "bitmap"
    filename: str
    wrap_mode: Literal["clamp", "repeat", "mirror"]


Textures = BitmapTexture