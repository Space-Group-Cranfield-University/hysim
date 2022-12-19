"""
Collection of classes that store and convert spectrum data
"""

from abc import ABC
from dataclasses import dataclass


@dataclass
class Spectrum(ABC):
    """Parent class for types of spectra

    Attributes
    ----------
    wavelengths: list
        List of wavelengths in spectrum

    Methods
    -------
    __len__
        Returns length of the spectrum
    crop_spectrum(min_wavelength, max_wavelength)
        Crop spectrum to min/max values (NOT IMPLEMENTED)
    resize_spectrum(spectrum_size)
        Interpolates data to specified number of bands (NOT IMPLEMENTED)
    create_value_comma_string(values)
        Make a comma seperated string of values from list
    """

    wavelengths: list

    def __len__(self) -> int:
        """Returns length of spectrum

        Returns
        -------
        int
            Length of spectrum point list
        """
        return len(self.wavelengths)

    def crop_spectrum(self, min_wavelength: float, max_wavelength: float):
        """Crop spectrum to min/max wavelengths

        Parameters
        ----------
        min_wavelength : float
            Minimum wavelength [nm]
        max_wavelength : float
            Maximum wavelength [nm]

        Raises
        ------
        NotImplementedError
            When called
        """
        raise NotImplementedError("Feature not yet implemented")

    def resize_spectrum(self, spectrum_size: int):
        """Creates polynomial of spectrum and remakes it with a given size

        Parameters
        ----------
        spectrum_size : int
            Length of the new spectrum

        Raises
        ------
        NotImplementedError
            When called
        """
        raise NotImplementedError("Feature not yet implemented")

    def create_value_comma_string(self, values: list) -> str:
        """Returns a string of comma seperated values from list

        Parameters
        ----------
        values : list
            List of values (usually float or int)

        Returns
        -------
        str
            Comma seperated string of values
        """
        string_values = [str(value) + "," for value in values]
        return "".join(string_values)[:-1]


@dataclass
class IrradianceSpectrum(Spectrum):
    """A spectrum of irradiance for given wavelengths

    Represents a spectrum of irradiance values with corresponding
    wavelengths. Inherits from Spectrum class

    Attributes
    ----------
    irradiance : list
        List of irradiance values

    Methods
    -------
    build_dict
        Build irregular spectrum dictionary for irradiance
    """

    irradiance: list

    def build_dict(self) -> dict:
        """Build irregular spectrum dictionary for irradiance

        Returns
        -------
        dict
            Irradiance spectrum dict
        """
        return {
            "type": "irregular",
            "wavelengths": self.create_value_comma_string(self.wavelengths),
            "values": self.create_value_comma_string(self.irradiance),
        }


@dataclass
class FilmSensitivitySpectrum(Spectrum):
    """A spectrum of film sensitivity for given wavelengths

    Represents a spectrum of film sensitivity (quantum efficiency)
    values with corresponding wavelengths. Inherits from Spectrum class.

    Attributes
    ----------
    sensitivities : list
        List of film sensitivities

    Methods
    -------
    band_name(lower_value, upper_value)
        Creates string describing upper and lower value seperated by an
        underscore
    build_dict
        Constructs dict for spectrum
    """

    sensitivities: list

    def band_name(self, lower_value: int, upper_value: int) -> str:
        """Creates string describing upper and lower value seperated by an
        underscore

        Returns
        -------
        str
            String of upper and lower values separated by underscore
        """
        return str(lower_value) + "_" + str(upper_value)

    def build_dict(self) -> dict:
        """Generates a dictionary for given number of bands

        Returns
        -------
        dict
            Dictionary representing film sensitivity spectrum
        """
        band_dict = {}

        for index, _ in enumerate(self.wavelengths[1:], start=1):
            band_dict.update(
                {
                    self.band_name(
                        self.wavelengths[index - 1], self.wavelengths[index]
                    ): {
                        "type": "irregular",

                        "wavelengths":
                                f"{self.wavelengths[index - 1]},\
                                  {self.wavelengths[index]}",

                        "values": str(self.sensitivities[index - 1])
                        + ","
                        + str(self.sensitivities[index]),
                    }
                }
            )

        return band_dict
