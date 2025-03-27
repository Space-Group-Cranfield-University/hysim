"""Simulator Module

This module contains the main run function for the simulator and classes to
handle Mitsuba.
"""
# Debugging
# import pretty_errors

# Logging
import logging

# Packages
import mitsuba as mi

# I/O
from hysim import input_data

# Package data
from hysim.data import data_handling as dh

# Simulator
from hysim import output_data
from hysim.configs.config import Config
from hysim.scene.builders import SceneBuilder
from hysim.scene import frame_transforms as frames, scene_builder as sb

class NoSceneLoaded(Exception):
    """Used to handle running a render without required data"""

    pass


class RendererControl:
    """Represents the render module

    Attributes
    ----------
    mitsuba_scene : object
        Mitsuba scene object
    params : SceneParameters
        Parameters in the scene represented by SceneParameters object
    render : TensorXf
        Output data from render represented by floating point tensor

    Methods
    -------
    load_scene(scene_dict)
        Loads scene dict into mitsuba and gets scene parameters
    run()
        Renders the scene using the loaded scene data

    """

    def __init__(self):
        """Initializer"""
        self.mitsuba_scene = None
        self.params = None
        self.render = None

    def load_scene(self, scene_dict: dict):
        """Loads scene dict into mitsuba and gets scene parameters

        Parameters
        ----------
        scene_dict : dict
            Dictionary containing all scene information
        """

        self.mitsuba_scene = mi.load_dict(scene_dict)
        self.params = mi.traverse(self.mitsuba_scene)

    def run(self):
        """Renders the loaded scene with mitsuba

        Raises
        -------
        NoSceneLoaded
            If the mitsuba_scene attribute is None

        """
        if self.mitsuba_scene is None:
            raise NoSceneLoaded("No scene to render")

        self.render = mi.render(self.mitsuba_scene)


def run_sim(run_directory: str):
    """Runs a single simulator case

    The function is called by the entry script to run a
    case. For a case the user input filed are parsed,
    the orbit data is converted to LVLH, and the scene is
    assembled. The scene is then rendered and the output
    is converted to the format specified in the configs.

    The run directory must be the root of the folders
    containing all configuration files.

    Parameters
    ----------
    run_directory : str
        Path to the case directory containing configuration
        files and user data.

    """

    logging.info("Running Simulation Case")
    # ------------------------------- #
    # Get user Inputs
    # ------------------------------- #
    logging.info("Getting user inputs from configuration files")



    user_inputs = input_data.Configs()
    user_inputs.load_configs(run_directory)
    kernel_paths = dh.get_kernel_paths()

    mi.set_variant(user_inputs.case_config["mitsuba_variant"])

    logging.info("Calculating scene geometry from orbit data")

    orbit_data = frames.MissionInputProcessor(
        user_inputs.mission_config, kernel_paths
    )
    # ------------------------------- #
    # Assemble Scene
    # ------------------------------- #
    logging.info("Building scene")
    scene = SceneBuilder(user_inputs, orbit_data)
    scene.build()

    def calculate_relative_distance(p1: list, p2: list):
        """Calculates relative distance between two points

        Calculates distance between two points in a 3d
        cartesian coordinate system.

        Parameters
        ----------
        p1 : list
            First set of coordinates in 3 dimensions [x,y,z]
        p2 : list
            Second set of coordinates in 3 dimensions [x,y,z]

        Returns
        -------
        float
            Distance between two points
        """
        return (
            (p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2
        ) ** (0.5)

    relative_distance = calculate_relative_distance(
        scene.chaser.position, scene.target.position
    )

    logging.debug(f"Chaser ECI Coordinates: {orbit_data.chaser_state_vectors}")

    logging.info("Relative distance to target: %0.2fm", relative_distance)

    # ------------------------------- #
    # Load to mitsuba and run
    # ------------------------------- #

    logging.debug("Final Scene Dictionary...")
    logging.debug(scene.scene_dict)

    logging.info("Loading scene into Mitsuba")

    sim = RendererControl()
    sim.load_scene(scene.scene_dict)
    logging.info("Scene assembled successfully")
    logging.info("Running Mitsuba")

    print("\n")
    sim.run()
    print("\n")

    logging.info("Render complete")
    # ------------------------------- #
    # Export Outputs
    # ------------------------------- #
    output = output_data.OutputHandler(
        sim.render,
        scene.chaser.sensor.film,
        run_directory,
    )
    output.produce_output_data(user_inputs)

def _set_mitsuba_logger():
    """Creates a custom formatter to match HySim and sets mitsuba's logger to use.
    Also sets the log level to mi.LogLevel.Info to make sure the start rendering and
    finished rendering messages are displayed."""
    class CustomMitsubaFormatter(mi.Formatter):
        def format(self, level: mi.LogLevel, thread, class_, file, line, msg):
            return f" {level.name.upper():8} Mitsuba - {msg}"

    # Note:  there is no progress bar if mi.variant() is a scalar varint
    mitsuba_logger = mi.Thread.thread().logger()
    mitsuba_logger.set_formatter(CustomMitsubaFormatter())
    mitsuba_logger.set_log_level(mi.LogLevel.Info)
    del mitsuba_logger


def run_sim2(run_directory: str):
    """Runs a single simulator case

    The function is called by the entry script to run a
    case. For a case the user input filed are parsed,
    the orbit data is converted to LVLH, and the scene is
    assembled. The scene is then rendered and the output
    is converted to the format specified in the configs.

    The run directory must be the root of the folders
    containing all configuration files.

    Parameters
    ----------
    run_directory : str
        Path to the case directory containing configuration
        files and user data.

    """

    logging.info("Running Simulation Case")

    # ------------------------------- #
    # Get user Inputs
    # ------------------------------- #
    logging.info("Getting user inputs from configuration files")

    config = Config(run_directory)
    kernel_paths = dh.get_kernel_paths()

    mi.set_variant(config.case.mitsuba_variant)


    logging.info("Calculating scene geometry from orbit data")
    position_data = frames.ScenePositionData(config.mission, kernel_paths)

    # ------------------------------- #
    # Assemble Scene
    # ------------------------------- #
    logging.info("Building scene")
    scene_builder = sb.SceneBuilder(config, position_data)

    logging.debug(f"Chaser ECI Coordinates: {position_data.chaser_position}")
    logging.info("Relative distance to target: %0.2fm", position_data.relative_distance)

    # ------------------------------- #
    # Load to mitsuba and run
    # ------------------------------- #
    scene_dict = scene_builder.scene.asdict
    logging.debug("Final Scene Dictionary...")
    logging.debug(scene_dict)

    logging.info("Adding case directory search paths to mitsuba")
    file_resolver = mi.Thread.thread().file_resolver()
    for path in config.directories:
        file_resolver.append(path)
        logging.debug("Added: " + path)
    del file_resolver

    logging.info("Loading scene into Mitsuba")
    sim = mi.load_dict(scene_dict)
    logging.info("Scene assembled successfully")
    logging.info("Running Mitsuba")

    _set_mitsuba_logger()
    print("")
    render: mi.TensorXf = mi.render(sim)
    print("")

    logging.info("Render complete")
    # ------------------------------- #
    # Export Outputs
    # ------------------------------- #
    output = output_data.OutputHandler2(render, scene_builder, config)
    output.export_data()

    logging.info("Done")
