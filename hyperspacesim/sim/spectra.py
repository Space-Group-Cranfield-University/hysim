'''
Collection of classes that store and convert spectrum data
'''

from abc import ABC
from dataclasses import dataclass


@dataclass
class Spectrum(ABC):
    '''A spectrum wavelengths'''
    wavelengths: list[float]

    def __len__(self):
        '''returns the length of the spectrum'''
        return len(self.wavelengths)


@dataclass
class FilmSensitivitySpectrum(Spectrum):
    '''A spectrum of film sensitivities and corresponding wavelengths'''
    sensitivities: list[float]

    def band_name(self, lower_value, upper_value):
        '''Creates string band name from two values with an _ between'''
        return str(lower_value) + "_" + str(upper_value)

    def build_dict(self):
        '''Generates a dictionary for given number of bands'''
        band_dict = {}

        for index, _ in enumerate(self.wavelengths[1:], start=1):
            band_dict.update({
                self.band_name(self.wavelengths[index-1], self.wavelengths[index]): {
                    "type": "spectrum",
                    "lambda_min": self.wavelengths[index-1],
                    "lambda_max": self.wavelengths[index],
                    "values": str(self.sensitivities[index-1])+","+str(self.sensitivities[index])
            }})

        return band_dict
