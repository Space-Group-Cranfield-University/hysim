"""Orbit frame transformation module

Module to handle transformations from input coordinates in various reference
frames to the local vertical local horizontal frame of the target.
"""
import numpy as np

# from dataclasses import dataclass
import spiceypy as spice

# Constants
MU_EARTH = 3.986004418e5


def calculate_eccentric_anomaly(
    eccentricity: float, true_anomaly: float
) -> float:
    """Calculates eccentric anomaly given eccentricity and true anomaly

    Parameters
    ----------
    eccentricity : float
        Eccentricity of an orbit [no units].
    true_anomaly : float
        True anomaly [rad]

    Returns
    -------
    float
        Eccentric anomaly of an orbit [rad]
    """
    return 2 * np.arctan(
        np.sqrt((1 - eccentricity) / (1 + eccentricity))
        * np.tan(true_anomaly / 2)
    )


def calculate_mean_anomaly(
    eccentric_anomaly: float, eccentricity: float
) -> float:
    """Calculates mean anomaly of an orbit given eccentric anomaly
    and eccentricity.

    Parameters
    ----------
    eccentric_anomaly : float
        Eccentric anomaly of the orbit [rad]
    eccentricity : float
        Eccentricity of the orbit [rad]

    Returns
    -------
    float
        Mean anomaly of the orbit [rad]
    """
    return eccentric_anomaly - eccentricity * np.sin(eccentric_anomaly)


def calculate_perifocal_distance(
    semi_major_axis: float, eccentricity: float
) -> list:
    """Calculates perifical distance of the orbit

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


def convert_kepler_to_state_vectors(elements: list, epoch: float) -> list:
    """Performs calculations to convert keplerian elements to state
    in ECI.

    State vectors contain:
    - Position vector (x, y, z) [m]
    - Velocity vector (vx, vy, vz) [m/s]

    Parameters
    ----------
    elements : list
        Keplerian elements describing the orbit in form:
        [a, e, i, raan, arg, nu]
    epoch : float
        Epoch at the imaging time TDB seconds past J2000

    Returns
    -------
    list
        State vectors as list [x, y, z, vx, vy, vz] [m/s]
    """
    perifocal_distance = calculate_perifocal_distance(elements[0], elements[1])

    # TODO: Confirm prefered input, uncomment this code to take in true anomaly
    # mean_anomaly = calculate_mean_anomaly(
    #     calculate_eccentric_anomaly(elements[1], elements[5]), elements[1]
    # )

    # TODO: Confirm prefered input, comment this out to swap to true anomaly
    mean_anomaly = elements[5]

    return spice.conics(
        [
            perifocal_distance,
            *elements[1:5],
            mean_anomaly,
            epoch,
            MU_EARTH,
        ],
        epoch,
    )


def check_for_null(tle_data: list) -> float:
    """Adds a null to first line of tle if there is not a null

    Parameters
    ----------
    tle_data : list
        List of tle strings

    Returns
    -------
    tle_data : list
        List of tle strings
    """
    if tle_data[0][-1] != "\x00":
        tle_data[0] += "\x00"
    return tle_data


def convert_tle_to_state_vectors(tle_data: list, epoch: float) -> list:
    """Converts two line element set to state vectors in ECI

    Parameters
    ----------
    tle_data : list
        List of tle strings
    epoch : float
        Epoch in seconds past J2000

    Returns
    -------
    list
        State vectors as list [x, y, z, vx, vy, vz] [m/s]
    """
    tle_data = check_for_null(tle_data)
    [_, tle_elements] = spice.getelm(1957, len(tle_data[0]), tle_data)
    geoph_data_list = ["J2", "J3", "J4", "KE", "QO", "SO", "ER", "AE"]
    geophs = [
        float(spice.bodvrd("EARTH", geoph_data, 1)[1])
        for geoph_data in geoph_data_list
    ]
    return spice.evsgp4(epoch, geophs, tle_elements)


def compute_eci_to_lvlh_rotation_matrix(state_vectors: list) -> np.array:
    """Determines rotation matrix used to convert ECI to LVLH

    Parameters
    ----------
    state_vectors : list
        State vectors as list [x, y, z, vx, vy, vz] [m/s]

    Returns
    -------
    array
        ECI -> LVLH transformation matrix
    """
    position = state_vectors[0:3]
    velocity = state_vectors[3:6]

    z_component = np.array(-position / np.linalg.norm(position))

    x_component = np.array(
        -np.cross(position, velocity)
        / np.linalg.norm(np.cross(position, velocity))
    )

    y_component = np.array(np.cross(z_component, x_component))

    return np.transpose(np.array([x_component, y_component, z_component]))


def convert_eci_to_lvlh(
    state_vectors: list, transform: np.array, origin: list
) -> list:
    """Converts position in ECI to LVLH frame

    Parameters
    ----------
    state_vectors : list
        State vectors as list [x, y, z, vx, vy, vz] [m/s]
    transform : np.array
        ECI -> LVLH transformation matrix
    origin : list
        Origin of LVLH frame

    Returns
    -------
    list
        Coordinates in LVLH frame
    """
    return (
        np.einsum("ij,i->j", transform, state_vectors[:3])
        + [
            0,
            0,
            np.linalg.norm(origin[:3]),
        ]
    ) * 1000


class MissionInputProcessor:
    """Handles mission inputs and converts to local coordinate system

    TODO: Decriptions

    Attributes
    ----------
    mission_config : dict
        User data defined in the mission config file
    epoch : float
        Time in seconds past J2000
    location_formats : dict
        Dictionary of valid conversions for user to choose
    target_state_vectors : list
        Orbit state vectors of the target
    chaser_state_vectors : list
        Orbit state vectors of the chaser
    sun_state_vectors : list
        Direction vector of sunlight from targets perspective
    earth_state_vectors : list
        State vector of Earth's position Default: [0,0,0]
    local_frame_transform : np.array
        Rotation matrix to covert ECI state vector to LVLH at target

    Methods
    -------
    get_sun_location()
        Calculates sun position from ephem data
    load_state_vectors(location_vector)
        Assign state vectors without conversion. This is only
        used in case where user defines orbit in ECI state vectors
    convert_input(scene_object)
        Use user inputs to choose conversion
    convert_inputs_to_state_vectors()
        Perform conversion for target, chaser and Sun (No conversion
        needed for Earth as already at [0,0,0] in ECI)
    target_position
        Property method for getting Target position in LVLH
    chaser_position
        Property method for getting Chaser position in LVLH
    earth_position
        Property method for getting Earth position in LVLH
    sun_direction_vector
        Property method for getting Sun direction vector
    """

    def __init__(self, mission_config: dict, kernel_paths: str):
        """Initializer

        Parameters
        ----------
        mission_config : dict
            Dictionary retrieved from mission config file
        kernel_paths : str
            Path to kernel
        """

        # Initialise Kernels
        spice.furnsh(kernel_paths)
        # Load configs
        self.mission_config = mission_config
        self.epoch = spice.str2et(mission_config["datetime"])
        self.location_formats = {
            "state": self.load_state_vectors,
            "kep": convert_kepler_to_state_vectors,
            "tle": convert_tle_to_state_vectors,
        }

        # Calculated state vectors
        self.target_state_vectors = []
        self.chaser_state_vectors = []
        self.sun_state_vectors = []
        self.earth_state_vectors = [0, 0, 0]

        # Load inputs and calculate state vectors
        self.convert_inputs_to_state_vectors()
        self.local_frame_transform = compute_eci_to_lvlh_rotation_matrix(
            self.target_state_vectors
        )

    def get_sun_location(self) -> list:
        """Get location of sun with respect to Earth at epoch

        Returns
        -------
        list
            Sun state vector
        """
        [sun_location, _] = spice.spkpos(
            "SUN", self.epoch, "J2000", "NONE", "EARTH"
        )
        return sun_location

    def load_state_vectors(self, location_vector: list, _) -> np.array:
        """Returns location state vector

        Parameters
        ----------
        location_vector : list
            Location in ECI (x,y,z)
        _ : None
            Dummy input

        Returns
        -------
        numpy.array
            location vector
        """
        return np.array(location_vector)

    def convert_input(self, scene_object: str) -> list:
        """Converts orbit defined in mission configs file to
        orbit state vectors

        Parameters
        ----------
        scene_object : str
            String stating object to be converted

        Returns
        -------
        list
            Orbit state vectors
        """
        input_format = self.mission_config[scene_object]["position_frame"]
        orbit_data = self.mission_config[scene_object]["position"]
        return self.location_formats[input_format](orbit_data, self.epoch)

    def convert_inputs_to_state_vectors(self):
        """Calls functions to convert user inputs to LVLH"""
        self.chaser_state_vectors = self.convert_input("chaser")
        self.target_state_vectors = self.convert_input("target")
        self.sun_state_vectors = self.get_sun_location()
        print(type(self.target_state_vectors))

    @property
    def target_position(self) -> list:
        """Returns target position in target centered LVLH

        Returns
        -------
        list
            Chaser position [x, y, z] [m]
        """
        return convert_eci_to_lvlh(
            self.target_state_vectors,
            self.local_frame_transform,
            self.target_state_vectors,
        )

    @property
    def chaser_position(self) -> list:
        """Returns chaser position in target centered LVLH

        Returns
        -------
        list
            Chaser position [x, y, z] [m]
        """
        return convert_eci_to_lvlh(
            self.chaser_state_vectors,
            self.local_frame_transform,
            self.target_state_vectors,
        )

    @property
    def earth_position(self) -> list:
        """Returns Earth position in target centered LVLH

        Returns
        -------
        list
            Earth position [x, y, z] [m]
        """
        return convert_eci_to_lvlh(
            self.earth_state_vectors,
            self.local_frame_transform,
            self.target_state_vectors,
        )

    @property
    def sun_direction_vector(self) -> list:
        """Returns Sun direction vector relative to target centered LVLH

        Returns
        -------
        list
            Sun direction vector
        """
        sun_position = convert_eci_to_lvlh(
            self.sun_state_vectors,
            self.local_frame_transform,
            self.target_state_vectors,
        )
        return -sun_position / np.linalg.norm(sun_position)
