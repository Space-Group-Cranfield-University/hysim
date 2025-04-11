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
import mitsuba.scalar_rgb as mit
import spiceypy as spice

# I/O
from pathlib import Path

# Package data
from hysim.data import data_handling as dh
from hysim import scene_builder as sb
from hysim import frame_transforms as ft

# Simulator
from hysim import output_data
from hysim.configs.config import Config


class RenderInstance:
    """Represents an instantaneous snapshot of the scene at a specified epoch"""

    output: mit.TensorXf
    scene_builder: sb.SceneBuilder
    position_data: ft.PositionData

    def __init__(self, config: Config, epoch: float):
        self.epoch = epoch
        self._config = config

    def build_scene(self):
        self.position_data = ft.PositionData(self._config.mission, self.epoch)
        self.scene_builder = sb.SceneBuilder(self._config, self.position_data)

    def render(self) -> mit.TensorXf:
        scene_dict = self.scene_builder.scene.asdict()
        sim: mit.Scene = mi.load_dict(scene_dict)
        print(mi.traverse(sim))
        self.output = mi.render(sim)
        return self.output


class RenderController:
    output: mit.TensorXf
    def __init__(self, config: Config, runs: int):
        self._config = config
        self.runs = runs
        self.base_epoch = spice.str2et(config.mission.datetime)
        self.instances = [RenderInstance(config, self.base_epoch)]

    def build_scenes(self):
        logging.info("Calculating scene geometry from orbit data")
        logging.info("Building scenes")
        for instance in self.instances:
            instance.build_scene()
            # logging.debug(f"Chaser ECI Coordinates: {instance.position_data.chaser_position}")
            # logging.info("Relative distance to target: %0.2fm", instance.position_data.relative_distance)
            # logging.debug("Final Scene Dictionary...")
            # logging.debug(instance.scene_builder.scene.asdict())

    def render(self) -> mit.TensorXf:
        logging.info("Adding case directory search paths to mitsuba")
        file_resolver = mi.Thread.thread().file_resolver()

        for path in self._config.directories:
            file_resolver.append(path)
            logging.debug("Added: " + path)
        del file_resolver

        self._set_mitsuba_logger()
        # logging.info("Loading scenes into Mitsuba")
        # logging.info("Running Mitsuba")
        # print("")
        self.output = self.instances[0].render()

        for instance in self.instances[1:]:
            self.output += instance.render()
        # print("")
        logging.info("Render complete")
        return self.output

    @staticmethod
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
    logging.info(f'Running Simulation Case @ "{run_directory}"')

    # ------------------------------- #
    # Get user Inputs
    # ------------------------------- #
    logging.info("Getting user inputs from configuration files")

    config = Config(run_directory)

    logging.info("Setting up SPICE kernels")
    spice.furnsh(dh.get_kernel_paths())

    mi.set_variant(config.case.mitsuba_variant)

    render_control = RenderController(config, 1)
    render_control.build_scenes()
    render_control.render()

    logging.info("Render complete")
    # ------------------------------- #
    # Export Outputs
    # ------------------------------- #
    output = output_data.OutputHandler(
        render_control.output, render_control.instances[0].scene_builder, config
    )
    output.export_data()

    logging.info("Done")
