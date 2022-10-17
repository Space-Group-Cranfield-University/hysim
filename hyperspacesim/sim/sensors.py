# Spectral Sensors
'''
doc string
'''

import numpy as np
import hyperspacesim.data as data

class SpectralBands:
    '''
    doc string
    '''

    def __init__(self, number_of_bands, spectral_response_file):
        self._spectral_response_file = spectral_response_file
        self._file_wavelengths = self.__get_wavelengths_from_file()
        self._file_sensitivities = self.__get_sensitivities_from_file()
        self._wavelengths = self.__define_wavelengths(number_of_bands)
        self._sensitivities = self.__compute_sensitivities()


    def __get_wavelengths_from_file(self):
        return data.SPDReader(file_location=self._spectral_response_file).wavelengths


    def __get_sensitivities_from_file(self):
        return data.SPDReader(file_location=self._spectral_response_file).sensitivities


    def __define_wavelengths(self, number_of_bands):
        wavelengths = np.linspace(
                start=self._file_wavelengths[0],
                stop=self._file_wavelengths[np.size(self._file_wavelengths)-1],
                num=number_of_bands
            ).astype(int)
        return wavelengths

    def __compute_sensitivities(self):
        band_sensitivities = np.interp(
                self._wavelengths,
                self._file_wavelengths,
                self._file_sensitivities
            )
        return band_sensitivities

    # Plotting methods
    def plot_spectrum(self):
        '''
        doc string
        '''
        return


    # Attribute getters
    @property
    def wavelengths(self):
        '''
        doc string
        '''
        return self._wavelengths.tolist()


    @property
    def sensitivities(self):
        '''
        doc string
        '''
        return self._sensitivities.tolist()


    @property
    def number_of_bands(self):
        '''
        doc string
        '''
        return len(self._wavelengths)


class SpectralSensor:
    def __init__(
            self,
            spectral_response_file,
            number_of_bands,
            film_resolution=(768, 576),
            component_format="float32",
        ):
        self.film_resolution = film_resolution
        self.component_format = component_format
        self.spectral_response = SpectralBands(number_of_bands, spectral_response_file)


class PerspectiveCamera(SpectralSensor):
    def __init__(
            self,
            sensor_name,
            spectral_response_file,
            number_of_bands,
            field_of_view,
            film_resolution=(768, 576),
            component_format="float16",
            focal_length = "50mm",
            fov_axis = "x",
            near_clip = 0.01,
            far_clip = 10000
        ):

        super().__init__(
            sensor_name,
            spectral_response_file,
            number_of_bands,
            film_resolution,
            component_format
        )

        self.field_of_view = field_of_view
        self.focal_length = focal_length
        self.fov_axis = fov_axis
        self.near_clip = near_clip
        self.far_clip = far_clip


class ThinLenseCamera(PerspectiveCamera):
    def __init__(
            self,
            sensor_name,
            spectral_response_file,
            number_of_bands,
            field_of_view,
            aperture_radius,
            film_resolution=(768, 576),
            component_format="float16",
            focal_length = "50mm",
            fov_axis = "x",
            near_clip = 0.01,
            far_clip = 10000,
            focus_distance = 0.0
        ):

        super().__init__(
            sensor_name,
            spectral_response_file,
            number_of_bands,
            field_of_view,
            film_resolution,
            component_format,
            focal_length,
            fov_axis,
            near_clip,
            far_clip
        )

        self.aperture_radius = aperture_radius
        self.focus_distance = focus_distance
