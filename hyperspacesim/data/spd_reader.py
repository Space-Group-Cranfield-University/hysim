'''
doc string
'''
# Utility functions for HyperSim
# # SPD File reader

class SPDReader:
    '''
    doc string
    '''
    _wavelength_column_index = 0
    _value_column_index = 1

    def __init__(self, file_location):
        self.file_location = file_location
        self._wavelengths = self.read_file_column(self._wavelength_column_index)
        self._values = self.read_file_column(self._value_column_index)

    def read_file_column(self, column):

        _string_list = [x.split()[column] for x in open(
                self.file_location,
                "r",
                encoding="utf_8"
            ).readlines()]

        return [float(x) for x in _string_list]

    @property
    def wavelengths(self):
        return self._wavelengths

    @property
    def values(self):
        return self._values
