"""Spectrum File Reader Module

Class to open and read .spd files and pass properties to user.
"""
# Utility functions for HyperSim
# # SPD File reader
import numpy as np


class SPDReader:
    """Manages data from .spd files

    Attributes
    ----------
    _wavelength_column_index : int
        Class attribute defining column containing wavelength in spd file
    _value_column_index : int
        Class attribute defining column containing value in spd file

    file_location : str
        Path to spd file
    _wavelengths : list[float]
        Wavelength values read from spectrum file
    _values : list[float]
        Values corresponding to each wavelength read from spectrum file

    Methods
    -------
    read_file_contents(column)
        Reads the contents of a utf-8 ascii file
    wavelengths
        Getter for wavelengths
    values
        Getter for values
    """

    _wavelength_column_index = 0
    _value_column_index = 1

    def __init__(self, file_location: str):
        """Initializer

        Parameters
        ----------
        file_location : str
            Path to file
        """
        self.file_location = file_location
        self._wavelengths = self.read_file_column(
            self._wavelength_column_index
        )
        self._values = self.gather_data_array()

    def gather_data_array(self):
        """Returns data in value columns (all except column 0)

        Walks through columns and gathers data for each in a numpy
        array.

        Returns
        -------
        np.array
            Array of value data for each band.

        """
        column_quantity = len(
            open(self.file_location, "r", encoding="utf_8")
            .readlines()[0]
            .split()
        )
        line_quantity = len(
            open(self.file_location, "r", encoding="utf_8").readlines()
        )
        file_data = np.zeros((line_quantity, column_quantity - 1))

        for column in range(1, column_quantity):
            file_data[:, column - 1] = self.read_file_column(column)

        return file_data

    def read_file_column(self, column):
        """Reads column in utf-8 file as a list

        Returns
        -------
        list
            List of rows returned from file for a given column
        """
        _string_list = [
            spectrum_file_line.split()[column]
            for spectrum_file_line in open(
                self.file_location, "r", encoding="utf_8"
            ).readlines()
        ]

        return [float(x) for x in _string_list]

    @property
    def wavelengths(self):
        """returns wavelengths"""
        """Getter for wavelengths

        Returns
        -------
        list
            Wavelengths
        """
        return self._wavelengths

    @property
    def values(self):
        """Getter for values in spectrum

        Returns
        -------
        np.array
            Values in spectrum
        """
        return np.squeeze(self._values)
