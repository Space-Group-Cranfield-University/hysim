'''
Collection of classes that store and convert spectrum data
'''

from abc import ABC
from dataclasses import dataclass


@dataclass
class Spectrum(ABC):
    '''A spectrum wavelengths'''
    wavelengths: list

    def __len__(self):
        '''returns the length of the spectrum'''
        return len(self.wavelengths)

    def crop_spectrum(self, min_wavelength, max_wavelength):
        '''Crops spectrum to an upper and lower value'''
        pass

    def resize_spectrum(self, spectrum_size):
        '''Creates polynomial of spectrum and remakes it with a given size'''
        pass

    def create_value_comma_string(self, values: list):
        '''Returns a string of comma seperated values'''
        string_values = [str(value) + "," for value in values]
        return "".join(string_values)[:-1]


@dataclass
class IrradianceSpectrum(Spectrum):
    '''A spectrum of irradiance for given wavelengths'''
    irradiance: list

    def build_dict(self):
        return {
            "type": "spectrum",
            "wavelengths": self.create_value_comma_string(self.wavelengths),
            "values": self.create_value_comma_string(self.irradiance),
        }



@dataclass
class FilmSensitivitySpectrum(Spectrum):
    '''A spectrum of film sensitivities for given wavelengths'''
    sensitivities: list

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
