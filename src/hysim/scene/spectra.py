"""
Collection of classes that store and convert spectrum data
"""

from abc import ABC
from dataclasses import dataclass
import numpy as np


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

    def string_values_from_array(self, values: np.array) -> str:
        """Returns a string of comma seperated values from numpy array

        Parameters
        ----------
        values : list
            List of values (usually float or int)

        Returns
        -------
        str
            Comma seperated string of values
        """
        return ", ".join(map(str, values))

    def band_name(self, lower_value: int, upper_value: int) -> str:
        """Creates string describing upper and lower value seperated by an
        underscore

        Returns
        -------
        str
            String of upper and lower values separated by underscore
        """
        return f"{str(lower_value)}_{str(upper_value)}"


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

    irradiance: np.array

    def __post_init__(self):
        """Post Initialiser method to check shape of data after init

        Raises
        ------
            TypeError if the number of columns in sensitivities array
            is greater than 1.
        """
        if self.irradiance.ndim != 1:
            raise TypeError("Too many columns for hyperspectral data")

    def build_dict(self) -> dict:
        """Build irregular spectrum dictionary for irradiance

        Returns
        -------
        dict
            Irradiance spectrum dict
        """
        return {
            "type": "irregular",
            "wavelengths": self.string_values_from_array(self.wavelengths),
            "values": self.string_values_from_array(self.irradiance),
        }


@dataclass
class HyperspectralFilmResponse(Spectrum):
    """A spectrum describing spectral response of hyperspectral film

    Represents a spectrum of film sensitivity (quantum efficiency)
    values with corresponding wavelengths. Inherits from Spectrum class.
    Build_dict method returns a dictionary containing a single narrow band
    for each wavelength. Each wavelength has a single response value. The
    total number of bands is determined by the number of data points.

    Attributes
    ----------
    sensitivities : numpy.array
        Array of film sensitivities

    Methods
    -------
    band_name(lower_value, upper_value)
        Creates string describing upper and lower value seperated by an
        underscore
    build_dict
        Constructs dict for spectrum
    """

    sensitivities: np.array

    def __post_init__(self):
        """Post Initialiser method to check shape of data after init

        Raises
        ------
            TypeError if the number of columns in sensitivities array
            is greater than 1.
        """
        if self.sensitivities.ndim != 1:
            raise TypeError("Too many columns for hyperspectral data")

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
                        # "wavelengths": f"{self.wavelengths[index - 1]},\
                        #           {self.wavelengths[index]}",
                        "wavelengths": self.string_values_from_array(
                            self.wavelengths[(index - 1): index + 1]
                        ),
                        # "values": str(self.sensitivities[index - 1])
                        # + ","
                        # + str(self.sensitivities[index]),
                        "values": self.string_values_from_array(
                            self.sensitivities[(index - 1): index + 1]
                        ),
                    }
                }
            )

        return band_dict


@dataclass
class MultispectralFilmResponse(Spectrum):
    """A spectrum of film sensitivity for multispectral film

    Represents a spectrum of film sensitivity (quantum efficiency)
    values with corresponding wavelengths. Inherits from Spectrum class.
    Each band contains spectral response over a wide range of wavelengths.
    The total number of bands is determined by the number of band response
    columns provided by the data file.

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

    sensitivities: np.array

    def build_dict(self) -> dict:
        """Generates a dictionary for given number of bands

        Returns
        -------
        dict
            Dictionary representing film sensitivity spectrum
        """
        band_dict = {}

        for i, band_data in enumerate(self.sensitivities.T):
            band_dict.update(
                {
                    f"Band_{i}": {
                        "type": "irregular",
                        "wavelengths": self.string_values_from_array(
                            self.wavelengths
                        ),
                        "values": self.string_values_from_array(band_data),
                    }
                }
            )

        return band_dict
