"""Output data module

This module contains classes to handle and format output render data from 
the simulator.
"""
import os
from itertools import tee

import mitsuba as mi
import numpy as np
import imageio as iio


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

        # Multispectral case
        if user_inputs.sensor_config["imaging_mode"] == "multispectral":
            # Find user input for band reference values
            try:
                channel_names = self.create_channel_names(
                    output_params["reference_wavelengths"]
                )
            except KeyError:
                print("reference_wavelengths required for multispectral .exr")

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
        result_bmp = mi.Bitmap(
            result_array,
            pixel_format=mi.Bitmap.PixelFormat.MultiChannel,
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
        if not os.path.isdir(output_params["file_name"]):
            os.mkdir(output_params["file_name"])
        else:
            # TODO: Logger here to say it already exists
            pass

        for i, _ in enumerate(self.render_data[0, 0, :]):
            dir_name = output_params["file_name"]
            band_name = f"Band_{i}.png"
            results_array = np.array(self.render_data[:, :, i])
            iio.imwrite(
                f"{dir_name}/{band_name}",
                # np.interp(
                #     results_array,
                #     (results_array.min(), results_array.max()),
                #     (0, 255),
                (results_array).astype(np.uint8),
            )

    def export_as_tiff(self, output_params):
        raise NotImplementedError("Tiff export not added")
