"""Output data module

This module contains classes to handle and format output render data from
the simulator.
"""
import logging
from pathlib import Path

import mitsuba as mi
import numpy as np
from PIL import Image
from drjit.auto import TensorXf

from hysim.configs.config import Config
from hysim.util.constants import ImagingMode, OutputFormat
from hysim.util.logging import log_level_context


def _log_exporting(output_format: OutputFormat):
    logging.info("Exporting results as a %s file", output_format.ext)


def _add_ext(file_path: Path, output_format: OutputFormat):
    if file_path.suffix != output_format.ext:
        file_path = file_path.with_suffix(output_format.ext)
    return file_path


def create_channel_names(wavelengths: list[float]) -> list[str]:
    """Generates list of channel names for the following
    exr header format: S0.xxx,xxnm where x is wavelength.
    """
    return [f"S0.{str(wavelength).replace('.', ',')}nm" for wavelength in wavelengths]


def export_exr(file_path: Path, render: TensorXf, wavelengths: list[float]):
    _log_exporting(OutputFormat.EXR)

    channel_names = create_channel_names(wavelengths)
    if len(channel_names) != render.shape[2]:
        raise ValueError("Total reference wavelengths and channels should be the same")

    if render.shape[2] == 1:
        pixel_format = mi.Bitmap.PixelFormat.Y
    else:
        pixel_format = mi.Bitmap.PixelFormat.MultiChannel

    bitmap = mi.Bitmap(
        render,
        pixel_format=pixel_format,
        channel_names=channel_names,
    )

    # TODO: add more metadata relevant to HySim. E.g. HySim version, frame count etc
    bitmap.metadata()["pixelAspectRatio"] = 1
    bitmap.metadata()["screenWindowWidth"] = 1

    file_path = _add_ext(file_path, OutputFormat.EXR)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if file_path.is_file():
        logging.info('The file "%s" already exists. Overwriting...', file_path)

    bitmap.write_async(str(file_path))


def export_bands(dir_path: Path, render: TensorXf, output_format: OutputFormat):
    """
    Export render data as bands in the specified format.

    Parameters
    ----------
    dir_path : Path
        The directory where the output files will be saved.
    render : TensorXf
        The render data from Mitsuba.
    output_format : OutputFormat
        The format in which the data should be exported (PNG or CSV).
    """
    if output_format == OutputFormat.EXR:
        raise ValueError(
            "Exporting bands to EXR format is not supported. Use export_exr instead."
        )

    _log_exporting(output_format)

    if dir_path.is_dir():
        logging.debug(
            'The directory "%s" already exists. The %s files inside may be overwritten.',
            dir_path,
            output_format.ext,
        )
    else:
        dir_path.mkdir(parents=True, exist_ok=True)

    file_writer = None
    if output_format == OutputFormat.PNG:
        file_writer = lambda file_path, data: mi.util.write_bitmap(str(file_path), data)
    elif output_format == OutputFormat.CSV:
        file_writer = lambda file_path, data: np.savetxt(file_path, np.array(data), delimiter=",")

    for i in range(render.shape[2]):
        file_writer(dir_path / f"band_{i}{output_format.ext}", render[:, :, i])


def export_gif(file_path: Path, render: TensorXf):
    _log_exporting(OutputFormat.GIF)
    file_path = _add_ext(file_path, OutputFormat.GIF)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    def write_frame(frame_index):
        bitmap = mi.util.convert_to_bitmap(render[..., frame_index])
        return Image.fromarray(np.asarray(bitmap))
        ## Exporting individual frames
        # path = str(file_path.parent / f"frame_{frame_index}.png")
        # mi.util.write_bitmap(path, render[..., frame_index], False)
        # return Image.open(path)

    with log_level_context(logging.INFO):
        images = [write_frame(index) for index in range(render.shape[3])]
        images[0].save(file_path, save_all=True, append_images=images[1:], duration=1000, loop=0)


def export(config: Config, data: TensorXf):
    for info in config.case.output:
        output_path = config.case_directory / Path(info.file_name)
        if info.format == OutputFormat.EXR:
            if config.sensor.imaging_mode == ImagingMode.HYPERSPECTRAL:
                wavelengths = [  # User rolling average of narrow band values
                    (spectrum.wavelengths[0] + spectrum.wavelengths[1]) / 2
                    for _, spectrum in config.sensor_bands
                ]
            else:  # imaging_mode == ImagingMode.MULTISPECTRAL:
                wavelengths = config.sensor.reference_wavelengths # Find user input for band reference values
            export_exr(output_path, data, wavelengths)
        elif info.format == OutputFormat.GIF:
            export_gif(output_path, data)
        else:
            export_bands(output_path, data, info.format)
