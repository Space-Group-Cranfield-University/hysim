"""Simulator Module

This module contains the main run function for the simulator and classes to
handle Mitsuba.
"""
# Debugging
# import pretty_errors

# Logging
import logging
from pathlib import Path

# Packages
import mitsuba as mi

# I/O
from hysim import frame_transforms as frames, scene_builder as sb

# Package data
from hysim.data import data_handling as dh

# Simulator
from hysim import output_data
from hysim.configs.config import Config


def _set_mitsuba_logger():
    """Creates a custom mitsuba formatter to match HySim and sets mitsuba's logger to use
    it. Also sets the log level to mi.LogLevel.Info to make sure the start and finished
    rendering messages are displayed."""
    class CustomMitsubaFormatter(mi.Formatter):
        def format(self, level: mi.LogLevel, thread, class_, file, line, msg):
            return f" {level.name.upper():8} Mitsuba - {msg}"

    # Note:  there is no progress bar if mi.variant() is noy a scalar varint
    mitsuba_logger = mi.Thread.thread().logger()
    mitsuba_logger.set_formatter(CustomMitsubaFormatter())
    mitsuba_logger.set_log_level(mi.LogLevel.Info)
    del mitsuba_logger


def run_sim(run_directory: Path):
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
    logging.info(f"Running Simulation Case @ \"{run_directory}\"");

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
    output = output_data.OutputHandler(render, scene_builder, config)
    output.export_data()

    logging.info("Done")
