"""Output data module

This module contains classes to handle and format output render data from
the simulator.
"""
import logging
from pathlib import Path
from typing import Final, Callable

import mitsuba as mi
import numpy as np
import imageio as iio

from hysim.configs.case_config import OutputItem
from hysim.configs.config import Config
from hysim.configs.constants import ImagingMode, OutputFormat
from hysim.scene_builder import SceneBuilder

class OutputHandler:
    """Formats data from the rendered scene and outputs it to a user specified location.

    Output data is converted to user defined format. Currently
    supported formats:
    - EXR
    - PNG
    - CSV
    """

    #def __init__(self, render_data: mi.TensorXf, scene_builder:SceneBuilder,  config: Config): #TODO: mitsuba import warning
    def __init__(self, render_data, scene_builder: SceneBuilder, config: Config):
        """Initializer

        Parameters
        ----------
        render_data : mi.TensorXf
            Tensor array output from mitsuba
        scene_builder : SceneBuilder
            The scene builder. Only used for getting spectra data with a hyperspectral
            imaging mode set.
        config : Config
            The user configuration object
        """
        self._render_data = render_data
        self._config = config
        self._scene_builder = scene_builder
        self._case_directory = Path(config.case_directory)
        self._log_prefix: Final[str] = "Exporting results as"
        self._format_map: dict[OutputFormat, Callable[[OutputItem], None]] = {
            OutputFormat.EXR: self._export_as_exr,
            OutputFormat.PNG: self._export_as_png,
            OutputFormat.CSV: self._export_as_csv,
        }

    def _create_output_directory(self, output_item: OutputItem) -> Path:
        result_dir = self._case_directory / output_item.file_name
        if result_dir.is_dir():
            logging.debug(
                f"The directory \"{result_dir}\" already exists. The .{output_item.format} files inside may be overwritten."
            )
        else:
            result_dir.mkdir(parents=True, exist_ok=True)
        return result_dir


    @staticmethod
    def _create_channel_names(wavelengths: list[float]) -> list[str]:
        """Generates list of channel names for the following
        exr header format: S0.xxx,xxnm where x is wavelength.
        """
        return [
            f"S0.{str(wavelength).replace('.', ',')}nm" for wavelength in wavelengths
        ]

    def _export_as_exr(self, output_item: OutputItem):
        logging.info(f"{self._log_prefix} a .{output_item.format} file")

        channel_names: list[str]
        if self._config.sensor.imaging_mode == ImagingMode.MULTISPECTRAL:
            # Find user input for band reference values
            try:
                channel_names = self._create_channel_names(
                    output_item.reference_wavelengths
                )
            except (KeyError, TypeError):
                logging.error("reference_wavelengths required for multispectral .exr")
        elif self._config.sensor.imaging_mode == ImagingMode.HYPERSPECTRAL:
            # User rolling average of narrow band values
            wavelengths = [
                (spectrum.wavelengths[0] + spectrum.wavelengths[1]) / 2
                for _, spectrum in self._scene_builder.spectra
            ]
            channel_names = self._create_channel_names(wavelengths)

        if len(channel_names) != len(self._render_data[0, 0, :]):
            raise ValueError(
                "Total reference wavelengths and channels should be the same"
            )

        if len(self._render_data[0, 0, :]) == 1:
            pixel_format = mi.Bitmap.PixelFormat.Y
        else:
            pixel_format = mi.Bitmap.PixelFormat.MultiChannel

        result_bmp = mi.Bitmap(
            self._render_data,
            pixel_format=pixel_format,
            channel_names=channel_names,
        )

        if "scalar" in mi.variant():
            # These assignments cause errors on cuda variants.
            result_bmp.metadata()["pixelAspectRatio"] = 1
            result_bmp.metadata()["screenWindowWidth"] = 1

        file_name = output_item.file_name
        exr = "." + OutputFormat.EXR
        if not file_name.endswith(exr):
            file_name += exr

        file_path = self._case_directory / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if file_path.is_file():
            logging.info(f"The file \"{file_path}\" already exists. Overwriting...")

        mi.util.write_bitmap(str(file_path), result_bmp)

    def _export_as_png(self, output_item: OutputItem):
        logging.info(f"{self._log_prefix} .{output_item.format} files")

        # output_item.file_name is actually a directory here
        results_dir = self._create_output_directory(output_item)

        for i in range(len(self._render_data[0, 0, :])):
            results_array = np.array(self._render_data[:, :, i])
            iio.imwrite(
                results_dir / f"Band_{i}.png",
                # np.interp(
                #      results_array,
                #      (results_array.min(), results_array.max()),
                #      (0, 255)),
                (results_array).astype(np.uint8),
                # prefer_uint8=False
                )

    def _export_as_csv(self, output_item: OutputItem):
        logging.info(f"{self._log_prefix} .{output_item.format} files")

        # output_item.file_name is actually a directory here
        results_dir = self._create_output_directory(output_item)

        for i in range(len(self._render_data[0, 0, :])):
            results_array = np.array(self._render_data[:, :, i])
            np.savetxt(
                results_dir / f"Band_{i}.csv", results_array, delimiter=","
            )

    def export_data(self):
        """For each format defined by user, export output data"""
        for output in self._config.case.output:
            self._format_map[output.format](output)
