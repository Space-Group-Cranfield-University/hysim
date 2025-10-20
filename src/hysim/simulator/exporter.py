"""Output data module

This module contains classes to handle and format output render data from
the simulator.
"""
import logging
from pathlib import Path
from typing import Union

import drjit as dr
import mitsuba as mi
import numpy as np
from PIL import Image
from drjit.auto import TensorXf

from hysim.configs.case_config import EXROutput, OutputItem, PNGOutput, CSVOutput, \
    GIFOutput
from hysim.configs.config import Config
from hysim.simulator.renderer import Render
from hysim.util.constants import ImagingMode
from hysim.util.logging import log_level


def _sum_frames(render: TensorXf, config: Config) -> TensorXf:
    return dr.sum(render, 3) * config.sensor.camera.dt

def _get_path(path: Path, config: Config) -> Path:
    if path.is_absolute():
        return path
    return config.case_directory / path

def _increment(path: Path, info: OutputItem):
    if info.overwrite:
       return path
    # Increment number at end of file if it exists.
    i = 1
    stem = path.stem.rstrip("_")
    while path.exists():
        path = path.with_stem(f"{stem}_{str(i)}")
        i += 1
    return path

def create_channel_names(wavelengths: list[float]) -> list[str]:
    """Generates list of channel names for the following
    exr header format: S0.xxx,xxnm where x is wavelength.
    """
    return [f"S0.{str(wavelength).replace('.', ',')}nm" for wavelength in wavelengths]


def export_exr(config: Config, render: TensorXf, info: EXROutput):
    if config.sensor.imaging_mode == ImagingMode.HYPERSPECTRAL:
        wavelengths = [  # User rolling average of narrow band values
            (spectrum.wavelengths[0] + spectrum.wavelengths[1]) / 2
            for _, spectrum in config.sensor_bands
        ]
    else:  # imaging_mode == ImagingMode.MULTISPECTRAL:
        wavelengths = config.sensor.reference_wavelengths  # Find user input for band reference values

    channel_names = create_channel_names(wavelengths)
    if len(channel_names) != render.shape[2]:
        raise ValueError("Total reference wavelengths and channels should be the same")

    if render.shape[2] == 1:
        pixel_format = mi.Bitmap.PixelFormat.Y
    else:
        pixel_format = mi.Bitmap.PixelFormat.MultiChannel

    file_path = _get_path(info.path, config)
    file_path = _increment(file_path, info)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    frame_count = render.shape[3]
    if info.frames and frame_count > 1:
        frames_dir = file_path.parent / f"frames_{info.ext.lstrip('.')}/"
        frames_dir = _increment(frames_dir, info)
        frames_dir.mkdir(exist_ok=True)
        logging.info('Exporting %s frames at "%s"', info.ext, frames_dir)
        for frame_index in range(render.shape[3]):
            mi.Bitmap(
                render[...,frame_index],
                pixel_format=pixel_format,
                channel_names=channel_names,
            ).write_async(str(frames_dir / f"frame_{frame_index}{info.ext}"))

    # ======================= #
    data = _sum_frames(render, config)
    # ======================= #

    bitmap = mi.Bitmap(
        data,
        pixel_format=pixel_format,
        channel_names=channel_names,
    )

    # TODO: add more metadata relevant to HySim. E.g. HySim version, frame count etc
    metadata = bitmap.metadata()
    metadata["pixelAspectRatio"] = 1
    metadata["screenWindowWidth"] = 1


    logging.info('Exporting %s at "%s"', info.ext, file_path)
    bitmap.write_async(str(file_path))

def export_bands(config: Config, render: TensorXf, info: Union[PNGOutput, CSVOutput]):
    dir_path = _get_path(info.path, config)
    dir_path = _increment(dir_path, info)
    dir_path.mkdir(parents=True, exist_ok=True)

    file_writer = None
    if isinstance(info, PNGOutput):
        file_writer = lambda file_path, data: mi.util.write_bitmap(str(file_path.with_suffix(info.ext)), data)
    elif isinstance(info, CSVOutput):
        file_writer = lambda file_path, data: np.savetxt(file_path.with_suffix(info.ext), np.array(data), delimiter=",")

    for i in range(render.shape[2]):
        file_writer(dir_path / f"band_{i}", render[:, :, i])


def export_gif(config: Config, render: TensorXf, info: GIFOutput):
    file_path = _get_path(info.path, config)
    file_path = _increment(file_path, info)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    frame_count = config.sensor.camera.frame_count
    if info.frames and frame_count > 1:
        frames_dir = file_path.parent / f"frames_{info.ext.lstrip('.')}/"
        frames_dir = _increment(frames_dir, info)
        frames_dir.mkdir(exist_ok=True)

    def write_frame(frame_index):
        bitmap = mi.util.convert_to_bitmap(render[..., frame_index])
        image = Image.fromarray(np.asarray(bitmap))
        if info.frames and frame_count > 1:
            image.save(frames_dir / f"frame_{frame_index}{PNGOutput.ext}")
        return image

    with log_level(logging.INFO): # Hide PIL debugs logs when in debug mode
        images = [write_frame(index) for index in range(frame_count)]
        duration = config.sensor.camera.dt * 1000 if info.frame_duration is None else info.frame_duration
        images[0].save(file_path, save_all=True, append_images=images[1:], duration=int(duration), loop=0)


def export(config: Config, data: Render):
    export_map = {
        EXROutput: lambda c,i: export_exr(c, data.spectral, i),
        PNGOutput: lambda c,i: export_bands(c, _sum_frames(data.spectral, c), i),
        CSVOutput: lambda c,i: export_bands(c, _sum_frames(data.spectral, c), i),
        GIFOutput: lambda c,i: export_gif(c, data.rgb, i),
    }

    for info in vars(config.case.output).values():
        if info is not None:
            logging.info("Exporting results as a %s file(s)", info.ext)
            export_map[type(info)](config, info)
