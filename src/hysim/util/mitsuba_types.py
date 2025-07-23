import mitsuba as mi
from typing_extensions import TypeAlias
import drjit.auto

if mi.variant() is None:
    try:
        import mitsuba.scalar_rgb as _mitsuba

        Transform: TypeAlias = _mitsuba.ScalarTransform4f
        Vector: TypeAlias = _mitsuba.Vector3f
    except ImportError:
        import importlib

        _mitsuba = importlib.import_module("mitsuba." + mi.variants()[0])
        Transform: TypeAlias = _mitsuba.ScalarTransform4f
        Vector: TypeAlias = _mitsuba.Vector3f
else:
    Transform: TypeAlias = mi.ScalarTransform4f
    Vector: TypeAlias = mi.Vector3f

Tensor: TypeAlias = drjit.auto.TensorXf