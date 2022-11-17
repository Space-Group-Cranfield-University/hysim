"""Module that handles IO for Mitsuba Renderer"""
import OpenEXR
import Imath
import numpy as np


class OutputHandler:
    def __init__(self, render_data, film_data, case_directory) -> None:
        self.output = OutputFormatter(render_data, film_data)
        self.case_directory = case_directory

    def produce_output_data(self, user_inputs):
        for output_selection in user_inputs.case_config["output"]:
            output_format = self.output.formats[output_selection["format"]]
            output_format(self.case_directory, output_selection["file_name"])


class OutputFormatter:
    def __init__(self, render_data, film_data) -> None:
        self.film_data = film_data
        self.render_data = render_data
        self.formats = {
            "exr": self.export_as_exr,
        }

    def export_as_exr(self, case_directory, output_file_name):
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
            (case_directory + output_file_name), exrHeader
        )
        exrImage.writePixels(channels_data)
