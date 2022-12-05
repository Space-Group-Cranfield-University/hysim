'''
Class to open and read .spd files and pass properties to user.
'''
# Utility functions for HyperSim
# # SPD File reader

class SPDReader:
    '''Opens and reads .spd files and exports the data'''
    _wavelength_column_index = 0
    _value_column_index = 1

    def __init__(self, file_location):
        self.file_location = file_location
        self._wavelengths = self.read_file_column(self._wavelength_column_index)
        self._values = self.read_file_column(self._value_column_index)

    def read_file_column(self, column):
        '''reads a column in the file'''
        _string_list = [x.split()[column] for x in open(
                self.file_location,
                "r",
                encoding="utf_8"
            ).readlines()]

        return [float(x) for x in _string_list]

    @property
    def wavelengths(self):
        '''returns wavelengths'''
        return self._wavelengths

    @property
    def values(self):
        '''returns values'''
        return self._values
