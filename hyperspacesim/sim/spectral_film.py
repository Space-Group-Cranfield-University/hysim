'''
Classes to define spectral film and produce mistuba ready dict
'''
import numpy as np
from hyperspacesim.data.spd_reader import SPDReader


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
        return SPDReader(file_location=self._spectral_response_file).wavelengths


    def __get_sensitivities_from_file(self):
        return SPDReader(file_location=self._spectral_response_file).values


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