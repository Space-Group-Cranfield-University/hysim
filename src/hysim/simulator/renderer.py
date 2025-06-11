import logging
from time import monotonic_ns as get_time
from typing import Final

import mitsuba as mi
import numpy as np
import spiceypy as spice

from hysim.configs import mission_config as mc
from hysim.configs.config import Config
from hysim.data import data_handling as dh
from hysim.simulator import frame_transforms as ft, scene_builder as sb
from hysim.util import mitsuba_types as mit
from hysim.util.logging import CustomMitsubaFormatter


class Frame:
    """Represents an instantaneous snapshot (a frame) of the scene at a specified epoch"""

    def __init__(self, epoch: ft.Epoch, mission_config: mc.MissionConfig, scene_builder: sb.SceneBuilder):
        self._output = None
        self.epoch: Final = epoch
        self.position_data: Final = ft.PositionData(mission_config, epoch)
        self.scene_dict: Final = scene_builder.set_positions(self.position_data)
        # logging.debug(f"Chaser ECI Coordinates: {self.position_data.chaser_position}")
        # logging.info("Relative distance to target: %0.2fm", self.position_data.relative_distance)
        # logging.debug("Final Scene Dictionary...")
        # logging.debug(scene_builder.scene.asdict())

    def render(self, frame_index: int = 0) -> mit.Tensor:
        sim: mi.Scene = mi.load_dict(self.scene_dict)
        with CustomMitsubaFormatter.log(frame_index):
            self._output = mi.render(sim)
        return self._output

    @property
    def output(self) -> mit.Tensor:
        return self._output


class RenderController:
    def __init__(self, config: Config):
        logging.info("Setting up SPICE kernels")
        spice.furnsh(dh.kernel_paths())

        mi.set_variant(config.case.mitsuba_variant)
        self.scene_builder = sb.SceneBuilder(config)
        self.output = mit.Tensor(np.zeros((
            config.sensor.film.height,
            config.sensor.film.width,
            len(self.scene_builder.spectra)
        )))
        self._config = config

        self.frame_count = config.sensor.camera.frame_count
        self.base_epoch = spice.str2et(config.mission.datetime)
        self.dt = config.sensor.camera.shutter_time / self.frame_count
        self.frames = []

    def render(self) -> mit.Tensor:
        logging.info("Building scene geometry")
        self.scene_builder.build()

        logging.info("Calculating scene positional data")
        self.frames = [
            Frame(
                ft.Epoch(self.base_epoch, self.dt * index),
                self._config.mission,
                self.scene_builder
            )
            for index in range(self.frame_count)
        ]
        logging.info("Adding case directory search paths to Mitsuba")

        file_resolver = mi.Thread.thread().file_resolver()
        for path in self._config.directories:
            file_resolver.append(path)
            logging.debug(f"{chr(0x02523)}{chr(0x02501)} {path}")
        del file_resolver

        logging.info("Running Mitsuba")
        t0 = get_time()

        for i, instance in enumerate(self.frames):
            # logging.info(chr(0x02501))
            self.output += instance.render(i) * self.dt
        t = (get_time() - t0) / 1e9
        duration = ""
        if round(t, 1) > 0: # and self.frame_count > 1:
            duration = f" (took {t:.2f}s)"
        logging.info(f"Renders complete.{duration}")
        return self.output
