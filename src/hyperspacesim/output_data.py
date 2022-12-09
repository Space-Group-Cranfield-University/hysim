"""Output data module

This module contains classes to handle and format output render data from 
the simulator.
"""
import OpenEXR
import Imath
import numpy as np


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
            output_format(output_selection["file_name"])


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
    export_as_exr(output_file_name)
        Exports rendered scene data in OpenEXR format
    """
    def __init__(self, render_data, film_data):
        """Initializer"""
        self.film_data = film_data
        self.render_data = render_data
        self.formats = {
            "exr": self.export_as_exr,
        }

    def export_as_exr(self, output_file_name: str):
        """Exports render data as .exr file

        Parameters
        ----------
        output_file_name : str
            Exported file name
        """
        bmp_array = np.array(self.render_data)
        exrHeader = OpenEXR.Header(self.film_data.width, self.film_data.height)

        channels = {}
        channels_data = {}

        for i, wavelength in enumerate(
            self.film_data.spectrum.wavelengths[:-1]
        ):
            channels.update(
                {
                    "S0."
                    + str(wavelength).replace(".", ",")
                    + "nm": Imath.Channel(Imath.PixelType(OpenEXR.FLOAT))
                }
            )
            channels_data.update(
                {
                    "S0."
                    + str(wavelength).replace(".", ",")
                    + "nm": bmp_array[:, :, i].tobytes()
                }
            )

        exrHeader["channels"] = channels
        exrHeader["spectralLayoutVersion"] = "1.0"
        exrHeader["emissiveUnits"] = "W.m^-2.sr^-1"

        exrImage = OpenEXR.OutputFile(
            (output_file_name), exrHeader
        )
        exrImage.writePixels(channels_data)
