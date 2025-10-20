import logging
from time import monotonic_ns as get_time
from typing import Any, Optional

import drjit as dr
import mitsuba as mi
import numpy as np
import spiceypy as spice
from drjit.auto import TensorXf

from hysim.configs.config import Config
from hysim.data import data_handling as dh
from hysim.simulator import frame_transforms as ft, scene_builder as sb
from hysim.util.logging import log_level_mitsuba, progress_bar, hysim_version, pretty


def render(config: Config) -> "Render":
    logging.info("Setting up SPICE kernels")
    spice.furnsh(dh.kernel_paths())
    mi.set_variant(config.case.mitsuba_variant)

    logging.info("Building scene geometry")
    scene_builder = sb.SceneBuilder(config)

    logging.info("Calculating scene positional data")
    epoch = spice.str2et(config.mission.datetime)
    frame_count = config.sensor.camera.frame_count
    dt = config.sensor.camera.dt
    position_data = [
        ft.PositionData(config.mission, ft.Epoch(epoch, dt * frame))
        for frame in range(frame_count)
    ]

    logging.info("Adding case directory search paths to Mitsuba")
    file_resolver = mi.Thread.thread().file_resolver()
    for path in config.directories:
        file_resolver.append(path)
    del file_resolver
    logging.debug("Directories:\n%s",pretty(config.directories))

    def render_frames(rgb: bool):
        if rgb:
            imaging_mode = "RGB"
            bands = 3
        else:
            imaging_mode = config.sensor.imaging_mode.capitalize()
            bands = len(config.sensor_bands)

        output: TensorXf
        description = f"Rendering [{imaging_mode}]:"
        output = dr.empty(
            TensorXf,
            (config.sensor.film.height, config.sensor.film.width, bands, frame_count),
        )

        with progress_bar(frame_count, description.ljust(26)) as (progress, task):
            for i in range(frame_count):
                scene_dict = scene_builder.set_positions(position_data[i], rgb)
                # progress.console.print("Chaser ECI Coordinates: %s", positions[i].eci.chaser)
                # progress.print(f"{level_format(logging.DEBUG)}Frame {i} - Chaser distance to target: {positions[i].relative_distance:0.2f}m")
                # progress.console.print("Final Scene Dictionary...")
                # progress.console.print(scene_builder.scene.asdict())
                scene: mi.Scene = mi.load_dict(scene_dict)

                with log_level_mitsuba(mi.LogLevel.Warn): # Hide Mitsuba progress bar when scalar variant
                    frame: TensorXf = mi.render(scene)

                output[..., i] = frame.array
                dr.eval(output)
                progress.advance(task)
        return output

    logging.info("Rendering with Mitsuba")
    t0 = get_time()

    data = Render()
    if config.case.output.requires_spectral:
        data.spectral = render_frames(False)
    if config.case.output.requires_rgb:
        data.rgb = render_frames(True)

    t = (get_time() - t0) / 1e9
    duration = ""
    if round(t, 1) > 0:  # and self.frame_count > 1:
        duration = f" (took {t:.2f}s)"
    logging.info(f"Renders complete.{duration}")

    if config.case.output.requires_spectral:
        data.create_metadata(config, position_data)
        logging.debug("Exr file metadata:\n%s",pretty(data.metadata))

    return data


class Render:
    def __init__(self):
        self.metadata: dict[str, Any] = {}
        self.frame_metadata: list[dict[str, Any]] = []
        self.spectral: Optional[TensorXf] = None
        self.rgb: Optional[TensorXf] = None
        # monochromatic: Optional[TensorXf] = None

    def create_metadata(self, config: Config, position_data: list[ft.PositionData]):
        frame_count = config.sensor.camera.frame_count
        self.frame_metadata = [
            {
                "hysim.version": hysim_version(),
                "hysim.sensor.frameCount": frame_count,
                "hysim.sensor.frameDuration": f"{config.sensor.camera.dt}s",
                "hysim.sensor.frameIndex": i,
                "hysim.sensor.fov": config.sensor.camera.field_of_view,
                "hysim.sensor.shutterTime": f"{config.sensor.camera.shutter_time}s",
                "hysim.eci.target": f"{np.array_str(position_data[i].eci.target/1000, precision=10)}km",
                "hysim.eci.chaser": f"{np.array_str(position_data[i].eci.chaser/1000, precision=10)}km",
                "hysim.eci.sun": f"{np.array_str(position_data[i].eci.sun/1000, precision=10)}km",
                "hysim.eci.targetToChaser": f"{position_data[i].relative_distance:.2f}m",
                "hysim.epoch": spice.et2utc(position_data[i].epoch, 'ISOC',2),
            }
            for i in range(frame_count)]
        self.metadata = dict(self.frame_metadata[0])
        del self.metadata["hysim.sensor.frameDuration"]
        if frame_count > 1:
            self.metadata["hysim.sensor.frameIndex"] = "all"
        else:
            del self.metadata["hysim.sensor.frameIndex"]