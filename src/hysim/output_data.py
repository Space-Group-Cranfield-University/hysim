"""Output data module

This module contains classes to handle and format output render data from
the simulator.
"""
import os
import logging
from itertools import tee
from typing import Final, Callable

import mitsuba as mi
import numpy as np
import imageio as iio

from hysim.configs.case_config import OutputItem
from hysim.configs.config import Config
from hysim.configs.constants import ImagingMode, OutputFormat
from hysim.scene.scene_builder import SceneBuilder


# Useful functions. TODO: During refactoring, move to utils module
def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def two_value_moving_average(values: list) -> list:
    """Creates moving average with a window size of two

    Parameters
    ----------
    values : list
        List of values to average

    Returns
    -------
    list
        Moving average result
    """
    return [(lower + higher) / 2 for lower, higher in pairwise(values)]


# Core Classes
class OutputHandler:
    """Handles output formatter

    Attributes
    ----------
    output : object
        Output data object, OutputFormatter
    case_directory : str
        Path to case directory

    Methods
    -------
    produce_output_data(user_inputs)
        For each format defined by user, export output data
    """

    def __init__(self, render_data, film_data, case_directory: str):
        """Initializer

        Parameters
        ----------
        render_data : TensorXf
            Tensor array output from renderer
        film_data : SpectralFilm
            Hyperspectral film object
        case_directory : str
            Path to case directory
        """
        self.output = OutputFormatter(render_data, film_data)
        self.case_directory = case_directory

    def produce_output_data(self, user_inputs):
        """Produces output files using data in OutputFormatter

        Parameters
        ----------
        user_inputs : object
            Input data from configuration files
        output_format : object
            Holds export function defined by user input
        """
        for output_selection in user_inputs.case_config["output"]:
            output_format = self.output.formats[output_selection["format"]]
            output_format(output_selection, user_inputs)


class OutputFormatter:
    """Formats output data from rendered scene

    Output data is converted to user defined format. Currently
    supported formats:
    - EXR

    Attributes
    ----------
    film_data : SpectralFilm
        Holds hyperspectral/multispectral film data
    render_data : TensorXf
        Tensor array output from renderer
    formats : dict
        Dictionary of export functions for each format

    Methods
    -------
    export_as_exr(output_params["file_name"])
        Exports rendered scene data in OpenEXR format
    """

    def __init__(self, render_data, film_data):
        """Initializer"""
        self.film_data = film_data
        self.render_data = render_data
        self.formats = {
            "exr": self.export_as_exr,
            "png": self.export_as_png,
            "csv": self.export_as_csv,
        }

    def create_channel_names(self, wavelengths: list) -> list:
        """Generates list of channel names for the following
        exr header format: S0.xxx,xxnm where x is wavelength.

        Parameters
        ----------
        wavelengths : list
            List of reference wavelengths used for channel name

        Returns
        -------
        channel_names : list(str)
            List of channel names.
        """
        channel_names = []

        for wavelength in wavelengths:
            wavelength_string = str(wavelength).replace(".", ",")
            channel_names.append(f"S0.{wavelength_string}nm")

        return channel_names

    def export_as_exr(self, output_params, user_inputs):
        """Exports render data as .exr file

        Parameters
        ----------
        output_params["file_name"] : str
            Exported file name
        user_inputs
            Object containing dictionaries of user inputs
        """

        logging.info("Exporting results as EXR File")

        # Multispectral case
        if user_inputs.sensor_config["imaging_mode"] == "multispectral":
            # Find user input for band reference values
            try:
                channel_names = self.create_channel_names(
                    output_params["reference_wavelengths"]
                )
            except KeyError:
                logging.error(
                    "reference_wavelengths required for multispectral .exr"
                )

        # Hyperspectral case
        elif user_inputs.sensor_config["imaging_mode"] == "hyperspectral":
            # User rolling average of narrow band values
            channel_names = self.create_channel_names(
                two_value_moving_average(self.film_data.spectrum.wavelengths)
            )

        if len(channel_names) != len(self.render_data[0, 0, :]):
            raise ValueError(
                "Total reference wavelengths and channels should be the same"
            )

        result_array = np.array(self.render_data)

        if len(self.render_data[0, 0, :]) == 1:
            pixel_format = mi.Bitmap.PixelFormat.Y
        else:
            pixel_format = mi.Bitmap.PixelFormat.MultiChannel

        result_bmp = mi.Bitmap(
            result_array,
            pixel_format=pixel_format,
            channel_names=channel_names,
        )

        result_bmp.metadata()["pixelAspectRatio"] = 1
        result_bmp.metadata()["screenWindowWidth"] = 1

        mi.util.write_bitmap(output_params["file_name"], result_bmp)

    def export_as_png(self, output_params: str, _):
        """Exports render data as .png files

        Parameters
        ----------
        output_params
            User provided output parameters
        """
        logging.info("Exporting results as PNG files")
        if not os.path.isdir(output_params["file_name"]):
            os.mkdir(output_params["file_name"])
        else:
            # TODO: Logger here to say it already exists
            pass

        for i in range(len(self.render_data[0, 0, :])):
            dir_name = output_params["file_name"]
            band_name = f"Band_{i}.png"
            results_array = np.array(self.render_data[:, :, i])
            iio.imwrite(
                f"{dir_name}/{band_name}",
                # np.interp(
                #      results_array,
                #      (results_array.min(), results_array.max()),
                #      (0, 255)),
                (results_array).astype(np.uint8),
                # prefer_uint8=False
            )

    def export_as_csv(self, output_params: str, _):
        """Exports render data as .csv files

        Parameters
        ----------
        output_params
            User provided output parameters
        """
        logging.info("Exporting results as CSV files")
        if not os.path.isdir(output_params["file_name"]):
            os.mkdir(output_params["file_name"])
        else:
            # TODO: Logger here to say it already exists
            pass

        for i in range(len(self.render_data[0, 0, :])):
            dir_name = output_params["file_name"]
            band_name = f"Band_{i}.csv"
            results_array = np.array(self.render_data[:, :, i])
            np.savetxt(
                f"{dir_name}/{band_name}", results_array, delimiter=","
            )

    def export_as_tiff(self, output_params):
        raise NotImplementedError("Tiff export not added")


class OutputHandler2:
    # def __init__(self, render_data: mi.TensorXf, scene_builder:SceneBuilder,  config: Config): TODO:
    def __init__(self, render_data, scene_builder:SceneBuilder,  config: Config):
        self.render_data = render_data
        self.config = config
        self.scene_builder = scene_builder
        self.case_directory = config.case_directory
        self.log_prefix: Final[str] = "Exporting results as ."
        self.results_dir: Final[str] = self._join_path(self.case_directory, "results")
        self.format_map: dict[OutputFormat, Callable[[OutputItem], None]] = {
            OutputFormat.EXR: self._export_as_exr,
            OutputFormat.PNG: self._export_as_png,
            OutputFormat.CSV: self._export_as_csv,
        }

    @staticmethod
    def _create_directory(directory:str) -> bool:
        """Returns true if a directory was created"""
        if not os.path.isdir(directory):
            os.mkdir(directory)
            return True
        return False

    def _create_output_directory(self, directory: str, output_format: OutputFormat):
        if not self._create_directory(directory):
            logging.info(
                f"{directory} already exists. The {output_format} files inside may be overwritten.")

    @staticmethod # maybe move to util module
    def _join_path(str1:str, str2:str)->str:
        return os.path.join(str1, str2).replace("\\", "/")

    @staticmethod
    def _create_channel_names(wavelengths: list[float]) -> list[str]:
        """Generates list of channel names for the following
        exr header format: S0.xxx,xxnm where x is wavelength.
        """
        return [f"S0.{str(wavelength).replace('.', ',')}nm" for wavelength in wavelengths]

    def _export_as_exr(self, output_item: OutputItem):
        logging.info(f"{self.log_prefix}{OutputFormat.EXR} file")

        channel_names: list[str]
        if self.config.sensor.imaging_mode == ImagingMode.MULTISPECTRAL:
            # Find user input for band reference values
            try:
                channel_names = self._create_channel_names(
                    output_item.reference_wavelengths
                )
            except KeyError:
                logging.error(
                    "reference_wavelengths required for multispectral .exr"
                )
        elif self.config.sensor.imaging_mode == ImagingMode.HYPERSPECTRAL:
            # User rolling average of narrow band values
            wavelengths = [(spectrum.wavelengths[0] + spectrum.wavelengths[1]) / 2
                           for spectrum in self.scene_builder.spectra]
            channel_names = self._create_channel_names(wavelengths)

        if len(channel_names) != len(self.render_data[0, 0, :]):
            raise ValueError(
                "Total reference wavelengths and channels should be the same"
            )

        if len(self.render_data[0, 0, :]) == 1:
            pixel_format = mi.Bitmap.PixelFormat.Y
        else:
            pixel_format = mi.Bitmap.PixelFormat.MultiChannel

        result_bmp = mi.Bitmap(
            self.render_data,
            pixel_format=pixel_format,
            channel_names=channel_names,
        )

        result_bmp.metadata()["pixelAspectRatio"] = 1
        result_bmp.metadata()["screenWindowWidth"] = 1

        file_name = output_item.file_name
        exr = "." + OutputFormat.EXR
        if not file_name.endswith(exr):
            file_name += exr

        self._create_directory(self.results_dir)
        file_path = self._join_path(self.results_dir, file_name)
        if os.path.isfile(file_path):
            logging.info(f"A {exr} file already exists. Overwriting...")

        mi.util.write_bitmap(file_path, result_bmp)

    def _export_as_png(self, output_item: OutputItem):
        logging.info(f"{self.log_prefix}{OutputFormat.PNG} files")

        self._create_directory(self.results_dir)
        png_dir = self._join_path(self.results_dir, output_item.file_name)
        self._create_output_directory(png_dir, OutputFormat.PNG)

        for i in range(len(self.render_data[0, 0, :])):
            band_name = f"Band_{i}.png"
            results_array = np.array(self.render_data[:, :, i])
            iio.imwrite(
                f"{png_dir}/{band_name}",
                # np.interp(
                #      results_array,
                #      (results_array.min(), results_array.max()),
                #      (0, 255)),
                (results_array).astype(np.uint8),
                # prefer_uint8=False
            )

    def _export_as_csv(self, output_item: OutputItem):
        logging.info(f"{self.log_prefix}{OutputFormat.CSV} files")

        self._create_directory(self.results_dir)
        csv_dir = self._join_path(self.results_dir, output_item.file_name)
        self._create_output_directory(csv_dir, OutputFormat.CSV)

        for i in range(len(self.render_data[0, 0, :])):
            band_name = f"Band_{i}.csv"
            results_array = np.array(self.render_data[:, :, i])
            np.savetxt(
                f"{csv_dir}/{band_name}", results_array, delimiter=","
            )

    def export_data(self):
        for output in self.config.case.output:
            self.format_map[output.format](output)


