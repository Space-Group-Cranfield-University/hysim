"""Orbit frame transformation module

Module to handle transformations from input coordinates in various reference
frames to the local vertical local horizontal frame of the target.
"""

from dataclasses import dataclass
from functools import cache
from typing import TypeVar, Generic, Final, Union

import numpy as np
import numpy.typing as npt
import spiceypy as spice

import hysim.configs.mission_config as mc
import hysim.util.mitsuba_types as mit
from hysim.util.constants import PositionFormat, SceneEntity

# Types
MVector = mit.Vector
MTransform = mit.Transform

NVector = npt.NDArray[np.float64]  #  np.ndarray[tuple[Literal[3]], np.ScalarType]
StateVector = npt.NDArray[np.float64]  # np.ndarray[tuple[Literal[6]], np.ScalarType]
RotationMatrix = npt.NDArray[np.float64]  # np.ndarray[tuple[Literal[3], Literal[3]], np.ScalarType]

# def calculate_eccentric_anomaly(
#     eccentricity: float, true_anomaly: float
# ) -> float:
#     """Calculates eccentric anomaly given eccentricity and true anomaly
#
#     Parameters
#     ----------
#     eccentricity : float
#         Eccentricity of an orbit [no units].
#     true_anomaly : float
#         True anomaly [rad]
#
#     Returns
#     -------
#     float
#         Eccentric anomaly of an orbit [rad]
#     """
#     return 2 * np.arctan(
#         np.sqrt((1 - eccentricity) / (1 + eccentricity))
#         * np.tan(true_anomaly / 2)
#     )
#
#
# def calculate_mean_anomaly(
#     eccentric_anomaly: float, eccentricity: float
# ) -> float:
#     """Calculates mean anomaly of an orbit given eccentric anomaly
#     and eccentricity.
#
#     Parameters
#     ----------
#     eccentric_anomaly : float
#         Eccentric anomaly of the orbit [rad]
#     eccentricity : float
#         Eccentricity of the orbit [rad]
#
#     Returns
#     -------
#     float
#         Mean anomaly of the orbit [rad]
#     """
#     return eccentric_anomaly - eccentricity * np.sin(eccentric_anomaly)


@cache
def mu_earth() -> float:
    """Returns the gravitational parameter of the Earth in km^3/s^2"""
    return spice.bodvrd("EARTH", "GM", 1)[1].item()


@cache
def geophysical_data() -> list[float]:
    return [
        spice.bodvrd("EARTH", geoph_data, 1)[1].item()
        for geoph_data in ["J2", "J3", "J4", "KE", "QO", "SO", "ER", "AE"]
    ]


def earth_radius() -> float:
    """Returns the radius of the Earth in meters"""
    return geophysical_data()[6] * 1000.0


def magnitude(vector: npt.NDArray) -> float:
    return np.linalg.norm(vector).item()


def normalise(vector: npt.NDArray) -> npt.NDArray:
    mag = magnitude(vector)
    if mag == 0: return vector
    return vector / mag


def calculate_perifocal_distance(semi_major_axis: float, eccentricity: float) -> float:
    """Calculates perifocal distance of the orbit

    Parameters
    ----------
    semi_major_axis : float
        Semi major axis of the orbit [m]
    eccentricity : float
        Eccentricity of the orbit [no units]

    Returns
    -------
    float
        Perifocal distance [m]
    """
    return semi_major_axis * np.abs(1 - eccentricity)


def kepler_to_state(kep_elements: list[float], epoch: float, epoch_delta: float = 0.0) -> StateVector:
    """Performs calculations to convert keplerian elements to state
    in ECI.

    State vectors contain:
    - Position vector (x, y, z) [m]
    - Velocity vector (vx, vy, vz) [m/s]

    Parameters
    ----------
    kep_elements : list[float]
        Keplerian elements describing the orbit in form:
        [a, e, i, raan, arg, nu]
    epoch : float
        Epoch at the imaging time TDB seconds past J2000
    epoch_delta : float
        Time since the base epoch in seconds
    Returns
    -------
    NStateVector
        State vectors as list [x, y, z, vx, vy, vz] [m/s]
    """
    perifocal_distance = calculate_perifocal_distance(kep_elements[0], kep_elements[1])

    # TODO: Confirm preferred input, uncomment this code to take in true anomaly
    # mean_anomaly = calculate_mean_anomaly(
    #     calculate_eccentric_anomaly(kep_elements[1], kep_elements[5]), kep_elements[1]
    # )

    # TODO: Confirm preferred input, comment this out to swap to true anomaly
    mean_anomaly = kep_elements[5]
    conic_elements = np.array(
        [perifocal_distance, *kep_elements[1:5], mean_anomaly, epoch, mu_earth()]
    )
    return spice.conics(conic_elements, epoch + epoch_delta) * 1000.0


def parse_tle(tle_data: list[str]) -> npt.NDArray[np.float64]:
    # Adds a null to first line of tle if there is not a null
    if tle_data[0][-1] != "\x00":
        tle_data[0] += "\x00"
    _, tle_elements = spice.getelm(1957, len(tle_data[0]), tle_data)
    return tle_elements


def tle_to_state(tle_data: list[str], epoch: float) -> StateVector:
    """Converts two line element set to state vectors in ECI

    Parameters
    ----------
    tle_data : list[str]
        List of tle strings
    epoch : float
        Epoch in seconds past J2000

    Returns
    -------
    NStateVector
        State vectors as list [x, y, z, vx, vy, vz] [m/s]
    float
        Mean motion of the orbit [rad/minute]
    """
    tle_elements = parse_tle(tle_data)

    return spice.evsgp4(epoch, geophysical_data(), tle_elements) * 1000.0


def rotation_matrix(state: StateVector) -> RotationMatrix:
    """Computes the rotation matrix for a state vector"""
    # Angular momentum of target
    pos = state[:3]
    vel = state[3:]
    angular_momentum = np.cross(pos, vel)

    # Unit vectors of the co-moving frame
    k = normalise(pos)
    j = normalise(-angular_momentum)
    i = np.cross(j, k)

    return np.array([i, j, k])


def clohessy_wiltshire(state: StateVector, omega: float, t: float) -> StateVector:
    tau = omega * t
    s = np.sin(tau)
    c = np.cos(tau)
    stm = np.array(
        [
            [4 - 3 * c, 0, 0, s / omega, (2 - 2 * c) / omega, 0],
            [6 * s - 6 * tau, 1, 0, (-2 + 2 * c) / omega, (4 * s - 3 * tau) / omega, 0],
            [0, 0, c, 0, 0, s / omega],
            [3 * omega * s, 0, 0, c, 2 * s, 0],
            [-6 * omega + 6 * c * omega, 0, 0, -2 * s, -3 + 4 * c, 0],
            [0, 0, -omega * s, 0, 0, c],
        ]
    )
    return stm @ state


def sun_state_vector(epoch: float) -> StateVector:
    """Get location of sun with respect to Earth at epoch

    Returns
    -------
    list
        Sun state vector
    """
    # Earth ID = 399
    # Sun ID = 10

    [sun_location, _] = spice.spkez(10, epoch, "J2000", "NONE", 399)
    return sun_location * 1000.0


def eci_to_frame(frame: RotationMatrix, frame_origin: NVector, state: StateVector) -> NVector:
    """Converts ECI state vector to LVLH position vector in the target centered
    reference frame"""

    displacement = frame_origin - state[:3]
    return frame @ displacement.T


def position_to_transform(position: NVector, attitude: list[float]) -> MTransform:
    return (
        MTransform()
        .translate(position)
        .rotate(axis=[1, 0, 0], angle=np.rad2deg(attitude[0]))
        .rotate(axis=[0, 1, 0], angle=np.rad2deg(attitude[1]))
        .rotate(axis=[0, 0, 1], angle=np.rad2deg(attitude[2]))
    )


_T = TypeVar("_T", npt.NDArray[np.float64], MTransform)


@dataclass(frozen=True)
class Positions(Generic[_T]):
    earth: _T
    sun: _T
    target: _T
    chaser: _T


class Epoch(float):
    """
    Epoch class to handle epoch time in seconds past J2000
    Attributes
    ----------
    base : float
        Time in seconds past J2000 of the initial frame
    delta : float
        Time since the base epoch in seconds
    """

    def __new__(cls, value: float, delta: float = 0.0):
        return super().__new__(cls, value + delta)

    def __init__(self, value: float, delta: float = 0.0):
        self.base: Final = value
        self.delta: Final = delta


class PositionData:
    def __init__(self, mission_config: mc.MissionConfig, epoch: Epoch):
        self._mission_config = mission_config
        self.epoch = epoch

        # noinspection PyArgumentList
        self.eci: Final = Positions[StateVector](  # ECI state vectors
            earth=np.zeros(6, dtype=np.float64),
            sun=sun_state_vector(epoch),
            target=self.to_state(mission_config.target),
            chaser=self.to_state(mission_config.chaser),
        )

        self._frame_transform = rotation_matrix(self.eci.target)

        if mission_config.chaser.position_frame == PositionFormat.STATE_LVLH:
            chaser_pos = self.eci.chaser[:3]
        else:
            chaser_pos = self._eci_to_target(self.eci.chaser)

        # noinspection PyArgumentList
        self.lvlh: Final = Positions[NVector](  # LVLH (target frame) position vectors
            earth=self._eci_to_target(self.eci.earth),
            sun=-normalise(self._eci_to_target(self.eci.sun)),
            target=self._eci_to_target(self.eci.target),
            chaser=chaser_pos,
        )

        if mission_config.chaser.is_lookat:
            chaser_transform = MTransform().look_at(
                origin=self.lvlh.chaser,
                target=self.lvlh.target,
                up=[0, 0, -1],  # Assumed +z is nadir
            )
        else:
            chaser_transform = (
                position_to_transform(self.lvlh.chaser, mission_config.chaser.attitude),
            )

        # noinspection PyArgumentList
        self.transforms: Final = Positions[MTransform](
            earth=MTransform().translate(self.lvlh.earth),
            sun=None,
            target=position_to_transform(
                self.lvlh.target, mission_config.target.attitude
            ),
            chaser=chaser_transform,
        )

    def to_state(self, satellite: mc.Spacecraft) -> StateVector:
        if satellite.position_frame == PositionFormat.STATE_ECI:
            return spice.prop2b(mu_earth(), np.asarray(satellite.position), self.epoch.delta)
        elif satellite.position_frame == PositionFormat.KEPLERIAN:
            return kepler_to_state(satellite.position, self.epoch.base, self.epoch.delta)
        elif satellite.position_frame == PositionFormat.TLE:
            return tle_to_state(satellite.position, self.epoch)
        elif satellite.position_frame == PositionFormat.STATE_LVLH and isinstance(satellite, mc.ChaserSpacecraft):
            return self.to_lvlh(np.asarray(satellite.position),self._mission_config.target,self.epoch.delta,)
        else:
            raise ValueError("Invalid position format")

    @staticmethod
    def to_lvlh(chaser_state: StateVector, target: mc.TargetSpacecraft, t: float) -> StateVector:
        """Calculates the chaser position in LVLH frame relative to the target.
        First the mean motion of the target is calculated depending on the type of
        input. This is then used with the Clohessy-Wiltshire equation to "propagate"
        the chaser satellite.
        """
        mean_motion: float  # rad/s
        if target.position_frame == PositionFormat.STATE_ECI:
            mu = mu_earth() * 1e9
            orbital_energy = magnitude(target[3:]) ** 2 / 2 - mu / magnitude(target[:3])
            semi_major_axis = -mu / (2 * orbital_energy)
            mean_motion = np.sqrt(mu / (semi_major_axis**3))
        elif target.position_frame == PositionFormat.KEPLERIAN:
            semi_major_axis = target.position[0]
            mean_motion = np.sqrt(mu_earth() / (semi_major_axis**3))
        elif target.position_frame == PositionFormat.TLE:
            tle = parse_tle(target.position)
            mean_motion = tle[8] / 60.0
        else:
            raise ValueError("Invalid position format")
        return clohessy_wiltshire(chaser_state, mean_motion, t)

    def _eci_to_target(self, state_vector: StateVector) -> NVector:
        return eci_to_frame(self._frame_transform, self.eci.target[:3], state_vector)

    def get(self, key: SceneEntity) -> Union[MTransform, MVector]:
        if key == SceneEntity.SUN:
            return MVector(self.lvlh.sun)
        return self.transforms.__dict__[key]
