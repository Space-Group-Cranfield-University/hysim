import logging
from time import monotonic_ns as get_time
from typing import Final

import drjit as dr
import mitsuba as mi
import spiceypy as spice

from hysim.configs import mission_config as mc
from hysim.configs.config import Config
from hysim.data import data_handling as dh
from hysim.simulator import frame_transforms as ft, scene_builder as sb
from hysim.util import mitsuba_types as mit, logging as lg


class Frame:
    """Represents an instantaneous snapshot (a frame) of the scene at a specified epoch"""
    #TODO: convert to function
    def __init__(self, epoch: ft.Epoch, mission_config: mc.MissionConfig, scene_builder: sb.SceneBuilder):

        self.epoch: Final = epoch
        self.position_data: Final = ft.PositionData(mission_config, epoch)
        self.scene_dict: Final = scene_builder.set_positions(self.position_data)
        # logging.debug(f"Chaser ECI Coordinates: {self.position_data.chaser_position}")
        # logging.info("Relative distance to target: %0.2fm", self.position_data.relative_distance)
        # logging.debug("Final Scene Dictionary...")
        # logging.debug(scene_builder.scene.asdict())

    def render(self, frame_index: int) -> mit.Tensor:
        sim: mi.Scene = mi.load_dict(self.scene_dict)
        with lg.CustomMitsubaFormatter.log(frame_index):
            output = mi.render(sim)
            lg.setdebugattr(self, "output", output)
            return output


def render(config: Config) -> mit.Tensor:
    logging.info("Setting up SPICE kernels")
    spice.furnsh(dh.kernel_paths())
    mi.set_variant(config.case.mitsuba_variant)


    logging.info("Building scene geometry")
    scene_builder = sb.SceneBuilder(config)
    scene_builder.build()

    logging.info("Calculating scene positional data")
    epoch = spice.str2et(config.mission.datetime)
    frame_count = config.sensor.camera.frame_count
    dt = config.sensor.camera.shutter_time / frame_count
    frames = [
        Frame(ft.Epoch(epoch, dt * i), config.mission, scene_builder)
        for i in range(frame_count)
    ]

    logging.info("Adding case directory search paths to Mitsuba")
    file_resolver = mi.Thread.thread().file_resolver()
    for path in config.directories:
        file_resolver.append(path)
        logging.debug(f"{chr(0x02523)}{chr(0x02501)} {path}")
    del file_resolver

    logging.info("Running Mitsuba")
    t0 = get_time()

    output: mit.Tensor = dr.zeros(
        mit.Tensor,
        (config.sensor.film.height,
         config.sensor.film.width,
         len(config.sensor_bands))
    )
    for i, instance in enumerate(frames):
        # logging.info(chr(0x02501))
        output += instance.render(i) * dt
    t = (get_time() - t0) / 1e9
    duration = ""
    if round(t, 1) > 0:  # and self.frame_count > 1:
        duration = f" (took {t:.2f}s)"
    logging.info(f"Renders complete.{duration}")
    return output
