import mitsuba as mi

from hysim.util.strenum import StrEnum


class ConfigType(StrEnum):
    """Enum of valid configuration types"""

    CASE = "case_config"
    MISSION = "mission_config"
    SENSOR = "sensor_config"
    PARTS = "parts_config"
    MATERIAL = "material_config"


MitsubaVariant = StrEnum(
    "MitsubaVariant", {str(variant).upper(): str(variant) for variant in mi.variants()}
)


class ImagingMode(StrEnum):
    """A spectrum of film sensitivity (quantum efficiency)"""

    HYPERSPECTRAL = "hyperspectral"
    """ Represents a single narrow band for each wavelength. Each wavelength has a 
    single response value. The total number of bands is determined by the number of 
    data points.
    """
    MULTISPECTRAL = "multispectral"
    """ Represents a single narrow band for each wavelength.  Each band contains 
    spectral response over a wide range of wavelengths. The total number of bands is 
    determined by the number of band response columns provided by the data file.
    """

class PositionFormat(StrEnum):
    STATE_ECI = "state"
    STATE_LVLH = "lvlh"
    KEPLERIAN = "kep"
    TLE = "tle"


class SceneEntity(StrEnum):
    """A list of entities that can be present in a scene"""
    EARTH = "earth"
    SUN = "sun"
    TARGET = "target"
    CHASER = "chaser"
