"""Module that handles IO for Mitsuba Renderer"""
import mitsuba as mi
import OpenEXR
import Imath
import numpy as np


class RendererControl:
    def __init__(self) -> None:
        self.mitsuba_scene = None
        self.params = None
        self.render = None

    def load_scene(self, scene_dict):
        self.mitsuba_scene = mi.load_dict(scene_dict)
        self.params = mi.traverse(self.mitsuba_scene)

    def run(self):
        self.render = mi.render(self.mitsuba_scene)


class OutputFormatter:
    def __init__(self, render_data) -> None:
        self.render_data = render_data

    def output_as_exr(self, film, case_directory):
        bmp_array = np.array(self.render)
        exrHeader = OpenEXR.Header(film.width, film.height)

        channels = {}
        channels_data = {}

        for i, wavelength in enumerate(film.spectrum.wavelengths[:-1]):
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

        exrImage = OpenEXR.OutputFile((case_directory + "output.exr"), exrHeader)
        exrImage.writePixels(channels_data)
