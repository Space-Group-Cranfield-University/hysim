"""Simulator Module

This module contains the main run function for the simulator and classes to
handle Mitsuba.
"""

# Debugging
# import pretty_errors

# Logging
import logging
from time import monotonic_ns as get_time
from contextlib import contextmanager

# Packages
import mitsuba as mi
import mitsuba.scalar_rgb as mit
import spiceypy as spice

# I/O
from pathlib import Path

# Package data
from hysim.data import data_handling as dh

# Simulator
from hysim import output_data
from hysim import scene_builder as sb
from hysim import frame_transforms as ft
from hysim.configs.config import Config


class CustomMitsubaFormatter(mi.Formatter):
    def __init__(self, frame_index: int):
        super().__init__()
        self.frame_index = frame_index

    def format(self, level: mi.LogLevel, thread, class_, file, line, msg):
        return f" {level.name.upper():8} {chr(0x02523)}{chr(0x02501)} Frame {self.frame_index} - {msg}"

    @staticmethod
    @contextmanager
    def log(frame_index: int):
        """Creates a custom mitsuba formatter to match HySim and sets mitsuba's logger to use
        it. Also sets the log level to mi.LogLevel.Info to make sure the start and finished
        rendering messages are displayed."""

        # NOTE: There is no progress bar displayed in the console if mi.variant() is not a scalar variant
        mitsuba_logger = mi.Thread.thread().logger()
        log_level = mitsuba_logger.log_level()
        try:
            mitsuba_logger.set_formatter(CustomMitsubaFormatter(frame_index))
            mitsuba_logger.set_log_level(mi.LogLevel.Info)
            yield
        finally:
            mitsuba_logger.set_log_level(log_level)
            del mitsuba_logger


class RenderInstance:
    """Represents an instantaneous snapshot (a frame) of the scene at a specified epoch"""

    def __init__(self, config: Config, epoch: ft.Epoch):
        self.epoch = epoch
        self._config = config
        self.output: mit.TensorXf = None
        self.position_data: ft.PositionData = None
        self.scene_dict = {}

    def build_scene(self, scene_builder: sb.SceneBuilder):
        self.position_data = ft.PositionData(self._config.mission, self.epoch)
        self.scene_dict = scene_builder.update_positions(
            self._config, self.position_data
        )

    def render(self, frame_index: int = 0) -> mit.TensorXf:
        sim: mit.Scene = mi.load_dict(self.scene_dict)
        with CustomMitsubaFormatter.log(frame_index):
            self.output = mi.render(sim)
        return self.output


class RenderController:
    def __init__(self, config: Config):
        self.output: mit.TensorXf = None
        self._config = config

        self.frame_count = config.sensor.camera.frame_count
        self.base_epoch = spice.str2et(config.mission.datetime)
        self.dt = config.sensor.camera.shutter_time / self.frame_count
        self.frames = [
            RenderInstance(config, ft.Epoch(self.base_epoch, self.dt * frame_index))
            for frame_index in range(self.frame_count)
        ]

        self.initial_frame = self.frames[0]
        logging.info("Calculating scene geometry from orbit data")
        self.initial_frame.position_data = ft.PositionData(config.mission, self.initial_frame.epoch)
        logging.info("Building initial scene geometry")
        self.scene_builder = sb.SceneBuilder(config, self.initial_frame.position_data)
        self.initial_frame.scene_dict = self.scene_builder.scene.asdict()

    def build_scenes(self):
        logging.info("Building remaining scenes")
        for frame in self.frames[1:]:
            frame.build_scene(self.scene_builder)
            # logging.debug(f"Chaser ECI Coordinates: {frame.position_data.chaser_position}")
            # logging.info("Relative distance to target: %0.2fm", frame.position_data.relative_distance)
            # logging.debug("Final Scene Dictionary...")
            # logging.debug(frame.scene_builder.scene.asdict())
        logging.info("Scene geometry built")

    def render(self) -> mit.TensorXf:
        logging.info("Adding case directory search paths to Mitsuba")
        file_resolver = mi.Thread.thread().file_resolver()

        for path in self._config.directories:
            file_resolver.append(path)
            logging.debug(f"{chr(0x02523)}{chr(0x02501)} {path}")
        else:
            logging.debug(f"{chr(0x02517)}{chr(0x02501)} {path}")
        del file_resolver

        # logging.info("Loading scene(s) into Mitsuba")
        logging.info("Running Mitsuba")
        self.output = self.initial_frame.render() * self.dt

        t0 = get_time()
        for i, instance in enumerate(self.frames[1:]):
            # logging.info(chr(0x02501))
            self.output += instance.render(i + 1) * self.dt
        t = (get_time() - t0) / 1e9
        duration = ""
        if round(t, 1) > 0 and self.frame_count > 1:
            duration = f" (took {t:.2f}s)"
        logging.info(f"Renders complete.{duration}")
        return self.output


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

    render_control = RenderController(config)
    render_control.build_scenes()
    render_control.render()
    # ------------------------------- #
    # Export Outputs
    # ------------------------------- #
    output = output_data.OutputHandler(
        render_control.output, render_control.scene_builder, config
    )
    output.export_data()

    logging.info("Done")
