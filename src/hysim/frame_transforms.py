"""Orbit frame transformation module

Module to handle transformations from input coordinates in various reference
frames to the local vertical local horizontal frame of the target.
"""

from functools import cache
from typing import Literal, NamedTuple

import numpy as np
import spiceypy as spice

from hysim.util.constants import PositionFormat
import hysim.configs.mission_config as mc
import hysim.util.mitsuba_types as mit
import mitsuba as mi

# Types
MVector = mit.Vector
MTransform = mit.Transform

NVector = np.ndarray[tuple[Literal[3]], np.ScalarType]
NStateVector = np.ndarray[tuple[Literal[6]], np.ScalarType]
NRotationMatrix = np.ndarray[tuple[Literal[3], Literal[3]], np.ScalarType]


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
    return spice.bodvrd("EARTH", "GM", 1)[1].item()


@cache
def geophysical_data():
    return [
        spice.bodvrd("EARTH", geoph_data, 1)[1].item()
        for geoph_data in ["J2", "J3", "J4", "KE", "QO", "SO", "ER", "AE"]
    ]


def magnitude(array: np.array) -> float:
    return np.linalg.norm(array).item()


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


def kepler_to_state(kep_elements: list[float], epoch: float) -> NStateVector:
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
    return spice.conics(conic_elements, epoch) * 1000.0


def parse_tle(tle_data: list[str]) -> np.ndarray[tuple[Literal[10]], np.float64]:
    # Adds a null to first line of tle if there is not a null
    if tle_data[0][-1] != "\x00":
        tle_data[0] += "\x00"
    _, tle_elements = spice.getelm(1957, len(tle_data[0]), tle_data)
    return tle_elements


def tle_to_state(tle_data: list[str], epoch: float) -> NStateVector:
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


def eci_to_lvlh_rotation_matrix(state: NStateVector) -> NRotationMatrix:
    # Angular momentum of target
    pos = state[:3]
    vel = state[3:]
    angular_momentum = np.cross(pos, vel)

    # Unit vectors of the co-moving frame
    k = pos / np.linalg.norm(pos)
    j = -angular_momentum / np.linalg.norm(-angular_momentum)
    i = np.cross(j, k)

    return np.array([i, j, k])


def clohessy_wiltshire(state: NStateVector, omega: float, t: float) -> NStateVector:
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


class Epoch(NamedTuple):
    """Epoch class to handle epoch time in seconds past J2000
    Attributes
    ----------
    base : float
        Time in seconds past J2000 of the initial frame
    offset : float
        Offset time in seconds
    """

    base: float
    offset: float

    @property
    def value(self) -> float:
        return self.base + self.offset


class PositionData:
    class StateVectors:
        """Calculates the state vectors of the Earth, Sun, Target and Chaser.
        All state vectors are in ECI frame. Unless the attribute
        ChaserSpacecraft.is_lvlh is true, in which case the chaser are in the LVLH
        relative to the target

        Attributes
        ----------
        epoch : Epoch
            The epoch of the simulation in seconds past J2000
        earth : NStateVector
            Earth state vector [0, 0, 0, 0, 0, 0] [m/s]
        sun : NStateVector
            Sun state vector [x, y, z, vx, vy, vz] [m/s]
        target : NStateVector
            Target state vector [x, y, z, vx, vy, vz] [m/s]
        chaser : NStateVector
            Chaser state vector [x, y, z, vx, vy, vz] [m/s]
        """

        def __init__(self, mission_config: mc.MissionConfig, epoch: Epoch):
            self.epoch = epoch
            self.earth: NStateVector = np.zeros(6, dtype=np.float64)
            self.target: NStateVector = self._convert_input(mission_config.target)

            if (
                mission_config.chaser.position_frame == PositionFormat.STATE
                and mission_config.chaser.is_lvlh
            ):
                self.chaser: NStateVector = self._chaser_lvlh(mission_config.target)
            else:
                self.chaser: NStateVector = self._convert_input(mission_config.chaser)

            self.sun: NStateVector = self._get_sun_location()

        def _convert_input(self, spacecraft: mc.Spacecraft) -> NStateVector:
            """Converts orbit defined in mission configs file to
            orbit state vectors

            Parameters
            ----------
            spacecraft : Spacecraft
                The Spacecraft object from mission config file

            Returns
            -------
            NVector
                Orbit state vectors
            """
            # TODO: validate spacecraft.position matches respective PositionFormat
            if spacecraft.position_frame == PositionFormat.STATE:
                return np.array(spacecraft.position)
            elif spacecraft.position_frame == PositionFormat.KEPLERIAN:
                return kepler_to_state(spacecraft.position, self.epoch.value)
            elif spacecraft.position_frame == PositionFormat.TLE:
                return tle_to_state(spacecraft.position, self.epoch.value)
            else:
                raise ValueError("Invalid position format")

        def _chaser_lvlh(self, target: mc.TargetSpacecraft) -> NStateVector:
            """Calculates the chaser position in LVLH frame relative to the target.
            First the mean motion of the target is calculated depending of the type of
            input. This is then used with the Clohessy-Wiltshire equation to "propagate"
            the chaser satellite.
            """
            mean_motion: float # rad/s
            if target.position_frame == PositionFormat.STATE:
                orbital_elements = spice.oscltx(
                    self.target / 1000.0, self.epoch.value, mu_earth()
                )
                orbital_period = orbital_elements[10]  # Orbital period in seconds
                if orbital_period == 0:
                    raise ValueError(
                        "Orbital period is zero. May be due to an eccentricity being close to 1"
                    )
                mean_motion = 2 * np.pi / orbital_period
            elif target.position_frame == PositionFormat.KEPLERIAN:
                semi_major_axis = target.position[0]
                mean_motion = np.sqrt(mu_earth() / (semi_major_axis**3))
            elif target.position_frame == PositionFormat.TLE:
                tle = parse_tle(target.position)
                mean_motion = tle[8] / 60.0
            else:
                raise ValueError("Invalid position format")
            return clohessy_wiltshire(self.target, mean_motion, self.epoch.offset)

        def _get_sun_location(self) -> NStateVector:
            """Get location of sun with respect to Earth at epoch

            Returns
            -------
            list
                Sun state vector
            """
            # Earth ID = 399
            # Sun ID = 10

            [sun_location, _] = spice.spkez(10, self.epoch.value, "J2000", "NONE", 399)
            return sun_location * 1000.0

    def __init__(self, mission_config: mc.MissionConfig, epoch: Epoch):
        self._mission_config = mission_config
        self._state_vectors = PositionData.StateVectors(mission_config, epoch)

        self._local_frame_transform = eci_to_lvlh_rotation_matrix(
            self._state_vectors.target
        )

        self._target_position = self._eci_to_lvlh(self._state_vectors.target)

        chaser = mission_config.chaser
        if chaser.position_frame == PositionFormat.STATE and chaser.is_lvlh:
            self._chaser_position = self._state_vectors.chaser[:3]
        else:
            self._chaser_position = self._eci_to_lvlh(self._state_vectors.chaser)

        self._earth_position = self._eci_to_lvlh(self._state_vectors.earth)

        sun_position = self._eci_to_lvlh(self._state_vectors.sun)
        self._sun_direction_vector = -sun_position / np.linalg.norm(sun_position)

    def _eci_to_lvlh(self, state_vector: NStateVector) -> NVector:
        """Converts ECI state vector to LVLH position vector in the target centered
        reference frame"""
        offset = self._state_vectors.target[:3] - state_vector[:3]
        return self._local_frame_transform @ offset.T

    @property
    def chaser_position(self) -> NVector:
        """Returns chaser position in target centered LVLH

        Returns
        -------
        Vector
            Chaser position [x, y, z] [m]

        """
        return self._chaser_position

    @property
    def sun_direction_vector(self) -> MVector:
        """Returns Sun direction vector relative to target centered LVLH
        Returns
        -------
        MVector
            Sun direction vector
        """
        return MVector(self._sun_direction_vector)

    @staticmethod
    def _get_spacecraft_transform(
        position: NVector, attitude: list[float]
    ) -> MTransform:
        return (
            mi.ScalarTransform4f()
            .translate(position)
            .rotate(axis=[1, 0, 0], angle=np.rad2deg(attitude[0]))
            .rotate(axis=[0, 1, 0], angle=np.rad2deg(attitude[1]))
            .rotate(axis=[0, 0, 1], angle=np.rad2deg(attitude[2]))
        )

    @property
    def earth_transform(self) -> MTransform:
        """Returns the mitsuba transformation matrix for the Earth"""
        return mi.ScalarTransform4f().translate(self._earth_position)

    @property
    def target_transform(self) -> MTransform:
        """Returns the mitsuba transformation matrix for the target"""
        return self._get_spacecraft_transform(
            self._target_position, self._mission_config.target.attitude
        )

    @property
    def chaser_transform(self) -> MTransform:
        """Returns the mitsuba transformation matrix for the chaser"""
        if self._mission_config.chaser.is_lookat:
            return mi.ScalarTransform4f().look_at(
                origin=self._chaser_position,
                target=self._target_position,
                up=[0, 0, -1],  # Assumed +z is nadir
            )
        else:
            return self._get_spacecraft_transform(
                self._chaser_position, self._mission_config.chaser.attitude
            )

    @property
    def relative_distance(self) -> float:
        """Calculates relative distance between the target and chaser in a 3d
        cartesian coordinate system."""
        return magnitude(self._target_position - self._chaser_position)
