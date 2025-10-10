"""Output data module

This module contains classes to handle and format output render data from
the simulator.
"""
import logging
import logging.handlers
from pathlib import Path

import drjit as dr
import mitsuba as mi
import numpy as np
from PIL import Image

import hysim.util.mitsuba_types as mit
from hysim.configs.config import Config
from hysim.util.constants import ImagingMode, OutputFormat
from hysim.util.logging import switch_log_level


def _log_exporting(output_format: OutputFormat):
    logging.info("Exporting results as a %s file", output_format.ext)


def _add_ext(file_name: Path, output_format: OutputFormat):
    if file_name.suffix != output_format.ext:
        file_name = file_name.with_suffix(output_format.ext)
    return file_name


def create_channel_names(wavelengths: list[float]) -> list[str]:
    """Generates list of channel names for the following
    exr header format: S0.xxx,xxnm where x is wavelength.
    """
    return [f"S0.{str(wavelength).replace('.', ',')}nm" for wavelength in wavelengths]


def export_exr(file_name: Path, case_directory: Path, render_data: mit.Tensor, wavelengths: list[float]):
    _log_exporting(OutputFormat.EXR)

    channel_names = create_channel_names(wavelengths)
    if len(channel_names) != len(render_data[0, 0, :]):
        raise ValueError("Total reference wavelengths and channels should be the same")

    if len(render_data[0, 0, :]) == 1:
        pixel_format = mi.Bitmap.PixelFormat.Y
    else:
        pixel_format = mi.Bitmap.PixelFormat.MultiChannel

    bitmap = mi.Bitmap(
        render_data,
        pixel_format=pixel_format,
        channel_names=channel_names,
    )

    # TODO: add more metadata relevant to HySim. E.g. HySim version, frame count etc
    bitmap.metadata()["pixelAspectRatio"] = 1
    bitmap.metadata()["screenWindowWidth"] = 1

    file_name = _add_ext(file_name, OutputFormat.EXR)

    file_path = case_directory / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if file_path.is_file():
        logging.info('The file "%s" already exists. Overwriting...', file_path)

    bitmap.write_async(str(file_path))


def export_bands(
    output_directory: Path,
    case_directory: Path,
    render_data: mit.Tensor,
    output_format: OutputFormat,
):
    """
    Export render data as bands in the specified format.

    Parameters
    ----------
    output_directory : Path
        Relative directory where the output files will be saved.
    case_directory : Path
        The directory where the case files are located.
    render_data : mit.Tensor
        The render data from Mitsuba.
    output_format : OutputFormat
        The format in which the data should be exported (PNG or CSV).
    """
    if output_format == OutputFormat.EXR:
        raise ValueError(
            "Exporting bands to EXR format is not supported. Use export_exr instead."
        )

    _log_exporting(output_format)

    path = case_directory / output_directory
    if path.is_dir():
        logging.debug(
            'The directory "%s" already exists. The %s files inside may be overwritten.',
            path,
            output_format.ext,
        )
    else:
        path.mkdir(parents=True, exist_ok=True)

    file_writer = None
    if output_format == OutputFormat.PNG:
        file_writer = lambda file_name, data: mi.util.write_bitmap(str(file_name), data)
    elif output_format == OutputFormat.CSV:
        file_writer = lambda file_name, data: np.savetxt(file_name, np.array(data), delimiter=",")

    for i in range(len(render_data[0, 0, :])):
        file_writer(path / f"band_{i}{output_format.ext}", render_data[:, :, i])


def export_gif(file_name: Path, case_directory: Path, render: dr.auto.TensorXf):
    _log_exporting(OutputFormat.GIF)
    file_path = _add_ext(file_name, OutputFormat.GIF)
    file_path = case_directory / file_path
    file_path.parent.mkdir(parents=True, exist_ok=True)

    def write_frame(frame_index):
        path = str(file_path.parent / f"frame_{frame_index}.png")
        mi.util.write_bitmap(path, render[..., frame_index], False)
        return Image.open(path)

    with switch_log_level(logging.INFO):
        images = [write_frame(index) for index in range(render.shape[3])]
        images[0].save(file_path, save_all=True, append_images=images[1:], duration=1000, loop=0)

def export(config: Config, data: mit.Tensor):
    for info in config.case.output:
        output_path = Path(info.file_name)
        if info.format == OutputFormat.EXR:
            if config.sensor.imaging_mode == ImagingMode.HYPERSPECTRAL:
                wavelengths = [  # User rolling average of narrow band values
                    (spectrum.wavelengths[0] + spectrum.wavelengths[1]) / 2
                    for _, spectrum in config.sensor_bands
                ]
            else:  # imaging_mode == ImagingMode.MULTISPECTRAL:
                wavelengths = config.sensor.reference_wavelengths # Find user input for band reference values
            export_exr(output_path, config.case_directory, data, wavelengths)
        elif info.format == OutputFormat.GIF:
            export_gif(output_path, config.case_directory, data)
        else:
            export_bands(output_path, config.case_directory, data, info.format)
