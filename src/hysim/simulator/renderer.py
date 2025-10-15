from __future__ import annotations

import logging
from time import monotonic_ns as get_time

import drjit as dr
import mitsuba as mi
import spiceypy as spice
from drjit.auto import TensorXf

from hysim.configs.config import Config
from hysim.data import data_handling as dh
from hysim.simulator import frame_transforms as ft, scene_builder as sb
from hysim.util.logging import log_level_mitsuba, progress_bar


class Render:
    spectral: TensorXf | None
    rgb: TensorXf | None
    # monochromatic: TensorXF | None

def render(config: Config) -> Render:
    logging.info("Setting up SPICE kernels")
    spice.furnsh(dh.kernel_paths())
    mi.set_variant(config.case.mitsuba_variant)

    logging.info("Building scene geometry")
    scene_builder = sb.SceneBuilder(config)

    logging.info("Calculating scene positional data")
    epoch = spice.str2et(config.mission.datetime)
    frame_count = config.sensor.camera.frame_count
    dt = config.sensor.camera.dt
    positions = [
        ft.PositionData(config.mission,ft.Epoch(epoch, dt * frame))
        for frame in range(frame_count)
    ]

    logging.info("Adding case directory search paths to Mitsuba")
    file_resolver = mi.Thread.thread().file_resolver()
    for path in config.directories:
        file_resolver.append(path)
        logging.debug(f"{chr(0x02523)}{chr(0x02501)} {path}")
    del file_resolver

    def render_frames(rgb: bool):
        output: TensorXf
        description = f" {'INFO':8} "
        height = config.sensor.film.height
        width = config.sensor.film.width
        if rgb:
            output = dr.empty(TensorXf,(height, width, 3, frame_count))
            description += "Rendering [RGB]:"
        else:
            output = dr.zeros(TensorXf,(height, width, len(config.sensor_bands)))
            description += f"Rendering [{config.sensor.imaging_mode.capitalize()}]:"

        with progress_bar(frame_count, description.ljust(36)) as (progress, task):
            for i in range(frame_count):
                scene_dict = scene_builder.set_positions(positions[i], rgb)
                # logging.debug(f"Chaser ECI Coordinates: {self.position_data.chaser_position}")
                # logging.info("Relative distance to target: %0.2fm", self.position_data.relative_distance)
                # logging.debug("Final Scene Dictionary...")
                # logging.debug(scene_builder.scene.asdict())
                scene: mi.Scene = mi.load_dict(scene_dict)

                with log_level_mitsuba(mi.LogLevel.Warn):
                    frame: TensorXf = mi.render(scene)

                if rgb:
                    output[..., i] = frame.array
                else:
                    output += frame * dt

                dr.eval(output)
                progress.advance(task)
        return output

    logging.info("Rendering with Mitsuba")
    t0 = get_time()

    data = Render()
    if config.case.requires_spectral:
        data.spectral = render_frames(False)
    if config.case.requires_rgb:
        data.rgb = render_frames(True)

    t = (get_time() - t0) / 1e9
    duration = ""
    if round(t, 1) > 0:  # and self.frame_count > 1:
        duration = f" (took {t:.2f}s)"
    logging.info(f"Renders complete.{duration}")
    return data
