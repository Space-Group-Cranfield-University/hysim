"""
Module to handle transformations from input coordinates in various reference
frames to the local vertical local horizontal frame of the target.
"""
import numpy as np

# from dataclasses import dataclass
import spiceypy as spice

# Constants
MU_EARTH = 3.986004418e5


def calculate_eccentric_anomaly(eccentricity, true_anomaly):
    return 2 * np.arctan(
        np.sqrt((1 - eccentricity) / (1 + eccentricity))
        * np.tan(true_anomaly / 2)
    )


def calculate_mean_anomaly(eccentric_anomaly, eccentricity):
    return eccentric_anomaly - eccentricity * np.sin(eccentric_anomaly)


def calculate_perifocal_distance(semi_major_axis, eccentricity):
    return semi_major_axis * np.abs(1 - eccentricity)


def convert_kepler_to_state_vectors(elements, epoch):
    perifocal_distance = calculate_perifocal_distance(elements[0], elements[1])
    mean_anomaly = calculate_mean_anomaly(
        calculate_eccentric_anomaly(elements[1], elements[5]), elements[1]
    )

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


def check_for_null(tle_data):
    """Adds a null to first line if there isnt one"""
    if tle_data[0][-1] != "\x00":
        tle_data[0] += "\x00"
    return tle_data


def convert_tle_to_state_vectors(tle_data, epoch):
    tle_data = check_for_null(tle_data)
    [_, tle_elements] = spice.getelm(1957, len(tle_data[0]), tle_data)
    geoph_data_list = ["J2", "J3", "J4", "KE", "QO", "SO", "ER", "AE"]
    geophs = [
        float(spice.bodvrd("EARTH", geoph_data, 1)[1])
        for geoph_data in geoph_data_list
    ]
    return spice.evsgp4(epoch, geophs, tle_elements)


def compute_eci_to_lvlh_rotation_matrix(state_vectors):
    position = state_vectors[0:3]
    velocity = state_vectors[3:6]

    z_component = np.array(-position / np.linalg.norm(position))

    x_component = np.array(
        -np.cross(position, velocity)
        / np.linalg.norm(np.cross(position, velocity))
    )

    y_component = np.array(np.cross(z_component, x_component))

    return np.transpose(np.array([x_component, y_component, z_component]))


def convert_eci_to_lvlh(state_vectors, transform, origin):
    return (
        np.einsum("ij,i->j", transform, state_vectors[:3])
        + [
            0,
            0,
            np.linalg.norm(origin[:3]),
        ]
    ) * 1000


class MissionInputProcessor:
    """Handles mission inputs and converts to local coordinate system"""

    def __init__(self, mission_config, kernel_path):
        # Initialise Kernels
        print(kernel_path)
        # kernel_path = "W:\\Work\\DASA_Hyperspectral_Simulator\\Code_Development\\hyperspacesim\\hyperspacesim\\data\\kernels\\meta_kernel.tm"
        spice.furnsh(kernel_path)

        # Load configs
        self.mission_config = mission_config
        self.epoch = spice.str2et(mission_config["datetime"])
        self.location_formats = {
            "state_vectors": self.load_state_vectors,
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

    def get_sun_location(self):
        [sun_location, _] = spice.spkpos(
            "SUN", self.epoch, "J2000", "NONE", "EARTH"
        )
        return sun_location

    def load_state_vectors(self, location_vector, _):
        return location_vector

    def convert_input(self, scene_object):
        input_format = self.mission_config[scene_object]["position_frame"]
        orbit_data = self.mission_config[scene_object]["position"]
        return self.location_formats[input_format](orbit_data, self.epoch)

    def convert_inputs_to_state_vectors(self):
        self.chaser_state_vectors = self.convert_input("chaser")
        self.target_state_vectors = self.convert_input("target")
        self.sun_state_vectors = self.get_sun_location()

    @property
    def target_position(self):
        return convert_eci_to_lvlh(
            self.target_state_vectors,
            self.local_frame_transform,
            self.target_state_vectors,
        )

    @property
    def chaser_position(self):
        return convert_eci_to_lvlh(
            self.chaser_state_vectors,
            self.local_frame_transform,
            self.target_state_vectors,
        )

    @property
    def earth_position(self):
        return convert_eci_to_lvlh(
            self.earth_state_vectors,
            self.local_frame_transform,
            self.target_state_vectors,
        )

    @property
    def sun_direction_vector(self):
        sun_position = convert_eci_to_lvlh(
            self.sun_state_vectors,
            self.local_frame_transform,
            self.target_state_vectors,
        )
        return -sun_position / np.linalg.norm(sun_position)
