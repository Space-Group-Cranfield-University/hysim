from __future__ import annotations

import logging
from time import monotonic_ns as get_time

import drjit as dr
import mitsuba as mi
import spiceypy as spice
from drjit.auto import TensorXf
from rich.progress import Progress, TimeElapsedColumn, \
    BarColumn, TextColumn, MofNCompleteColumn, SpinnerColumn

from hysim.configs.config import Config
from hysim.data import data_handling as dh
from hysim.simulator import frame_transforms as ft, scene_builder as sb
from hysim.util.logging import log_level_context_mitsuba


# class Frame:
#     """Represents an instantaneous snapshot (a frame) of the scene at a specified epoch"""
#     #TODO: convert to function
#     def __init__(self, epoch: ft.Epoch, mission_config: mc.MissionConfig, scene_builder: sb.SceneBuilder):
#
#         self.epoch: Final = epoch
#         self.position_data: Final = ft.PositionData(mission_config, epoch)
#         self.scene_dict: Final = scene_builder.set_positions(self.position_data)
#         # logging.debug(f"Chaser ECI Coordinates: {self.position_data.chaser_position}")
#         # logging.info("Relative distance to target: %0.2fm", self.position_data.relative_distance)
#         # logging.debug("Final Scene Dictionary...")
#         # logging.debug(scene_builder.scene.asdict())
#
#     def render(self, frame_index: int) -> mit.Tensor:
#         sim: mi.Scene = mi.load_dict(self.scene_dict)
#
#         with lg.CustomMitsubaFormatter.log(frame_index):
#             output = mi.render(sim)
#             lg.setdebugattr(self, "output", output)
#             return output

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
            bar_width = 50
        else:
            output = dr.zeros(TensorXf,(height, width, len(config.sensor_bands)))
            description += f"Rendering [{config.sensor.imaging_mode.capitalize()}]:"
            bar_width = 40

        if frame_count == 1:
            total = None
            columns = (
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width),
                TimeElapsedColumn(),
            )
        else:
            total = frame_count
            columns = (
                TextColumn("[progress.description]{task.description}"),
                SpinnerColumn(),
                BarColumn(bar_width),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
            )
        with Progress(*columns) as progress:
            task = progress.add_task(description,total = total)
            for i in range(frame_count):
                scene_dict = scene_builder.set_positions(positions[i], rgb)
                scene: mi.Scene = mi.load_dict(scene_dict)

                with log_level_context_mitsuba(mi.LogLevel.Warn):
                    frame: TensorXf = mi.render(scene)

                if rgb:
                    output[..., i] = frame.array
                else:
                    output += frame * dt

                dr.eval(output)
                progress.advance(task)
            progress.update(task,description=description.replace("Rendering", "Completed"))
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


# def render_frames(config: Config, scene_builder, positions, rgb: bool, progress: Progress, task: TaskID, data:Render):
#     dt = config.sensor.camera.dt
#     frame_count = config.sensor.camera.frame_count
#     output: TensorXf
#     height = config.sensor.film.height
#     width = config.sensor.film.width
#     if rgb:
#         output = dr.empty(TensorXf,(height, width, 3, frame_count))
#     else:
#         output = dr.zeros(TensorXf,(height, width, len(config.sensor_bands)))
#
#     for i in range(frame_count):
#         scene_dict = scene_builder.set_positions(positions[i], rgb)
#         scene: mi.Scene = mi.load_dict(scene_dict)
#
#         #with lg.log_level_context_mitsuba(mi.LogLevel.Warn):
#         frame: TensorXf = mi.render(scene)
#
#         if rgb:
#             output[..., i] = frame.array
#         else:
#             output += frame * dt
#         progress.advance(task)
#     columns = (
#         TextColumn("[progress.description]{task.description}"),
#         BarColumn(),
#         TaskProgressColumn(),
#         TimeElapsedColumn()
#     )
#     with Progress(*columns) as progress:
#         task = progress.add_task("Moving Data", total=1)
#         if rgb:
#             data.rgb = output
#         else:
#             data.spectral = output  # THIS Opperation is incredibly slow. Takes a long time. Maybe is cos im using dr.auto.TensorXf, and this is when the rendering actually takes place. IT ISSSS adding a dr.eval made everthing work
#         progress.advance(task)
#
#     pass
#     # return output


# def render_frames(config: Config, scene_builder, positions, rgb: bool):
#     dt = config.sensor.camera.dt
#     frame_count = config.sensor.camera.frame_count
#     output: TensorXf
#     description = f" {'INFO':8} "
#     height = config.sensor.film.height
#     width = config.sensor.film.width
#     if rgb:
#         output = dr.empty(TensorXf,(height, width, 3, frame_count))
#         description += "Rendering [RGB]"
#     else:
#         output = dr.zeros(TensorXf,(height, width, len(config.sensor_bands)))
#         description += f"Rendering [{config.sensor.imaging_mode.capitalize()}]"
#
#     if frame_count == 1:
#         total = None
#     else:
#         total = frame_count
#     columns = (
#         TextColumn("[progress.description]{task.description}"),
#         BarColumn(),
#         TaskProgressColumn(),
#         TimeElapsedColumn()
#     )
#     with Progress(*columns) as progress:
#         task = progress.add_task(description,total = total)
#         for i in range(frame_count):
#             scene_dict = scene_builder.set_positions(positions[i], rgb)
#             scene: mi.Scene = mi.load_dict(scene_dict)
#
#             #with lg.log_level_context_mitsuba(mi.LogLevel.Warn):
#             frame: TensorXf = mi.render(scene)
#
#             if rgb:
#                 output[..., i] = frame.array
#             else:
#                 output += frame * dt
#             progress.advance(task)
#
#     return output

# def render(config: Config) -> mit.Tensor:
#     logging.info("Setting up SPICE kernels")
#     spice.furnsh(dh.kernel_paths())
#     mi.set_variant(config.case.mitsuba_variant)
#
#     logging.info("Building scene geometry")
#     scene_builder = sb.SceneBuilder(config)
#
#     logging.info("Calculating scene positional data")
#     epoch = spice.str2et(config.mission.datetime)
#     frame_count = config.sensor.camera.frame_count
#     dt = config.sensor.camera.shutter_time / frame_count
#
#     logging.info("Adding case directory search paths to Mitsuba")
#     file_resolver = mi.Thread.thread().file_resolver()
#     for path in config.directories:
#         file_resolver.append(path)
#         logging.debug(f"{chr(0x02523)}{chr(0x02501)} {path}")
#     del file_resolver
#
#     logging.info("Running Mitsuba")
#     t0 = get_time()
#
#     output: TensorXf = dr.empty(
#         TensorXf,
#         (config.sensor.film.height,
#          config.sensor.film.width,
#          3,
#          frame_count)
#     )
#
#     for i in range(frame_count):
#         position_data = ft.PositionData(config.mission,ft.Epoch(epoch, dt * i))
#         scene_dict = scene_builder.set_positions(position_data, True)
#         scene: mi.Scene = mi.load_dict(scene_dict)
#
#         data: TensorXf = mi.render(scene)
#         output[...,i] = data.array
#
#     t = (get_time() - t0) / 1e9
#     duration = ""
#     if round(t, 1) > 0:  # and self.frame_count > 1:
#         duration = f" (took {t:.2f}s)"
#     logging.info(f"Renders complete.{duration}")
#     return output
#


# def render(config: Config) -> mit.Tensor:
#     logging.info("Setting up SPICE kernels")
#     spice.furnsh(dh.kernel_paths())
#     mi.set_variant(config.case.mitsuba_variant)
#
#     logging.info("Building scene geometry")
#     scene_builder = sb.SceneBuilder(config)
#
#     logging.info("Calculating scene positional data")
#     epoch = spice.str2et(config.mission.datetime)
#     frame_count = config.sensor.camera.frame_count
#     dt = config.sensor.camera.shutter_time / frame_count
#
#
#     frames = [
#         Frame(ft.Epoch(epoch, dt * i), config.mission, scene_builder)
#         for i in range(frame_count)
#     ]
#
#     logging.info("Adding case directory search paths to Mitsuba")
#     file_resolver = mi.Thread.thread().file_resolver()
#     for path in config.directories:
#         file_resolver.append(path)
#         logging.debug(f"{chr(0x02523)}{chr(0x02501)} {path}")
#     del file_resolver
#
#     logging.info("Running Mitsuba")
#     t0 = get_time()
#
#     output: mit.Tensor = dr.zeros(
#         mit.Tensor,
#         (config.sensor.film.height,
#          config.sensor.film.width,
#          len(config.sensor_bands))
#     )
#     for i, instance in enumerate(frames):
#         # logging.info(chr(0x02501))
#         output += instance.render(i) * dt
#     t = (get_time() - t0) / 1e9
#     duration = ""
#     if round(t, 1) > 0:  # and self.frame_count > 1:
#         duration = f" (took {t:.2f}s)"
#     logging.info(f"Renders complete.{duration}")
#     return output
