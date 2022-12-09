"""Spectrum File Reader Module

Class to open and read .spd files and pass properties to user.
"""
# Utility functions for HyperSim
# # SPD File reader


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
        self._values = self.read_file_column(self._value_column_index)

    def read_file_column(self, column):
        """Reads column in utf-8 file as a list

        Returns
        -------
        list
            List of rows returned from file for a given column
        """
        _string_list = [
            x.split()[column]
            for x in open(
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
        list
            Values in spectrum
        """
        return self._values
