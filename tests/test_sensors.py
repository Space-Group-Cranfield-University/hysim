
import unittest
from hysim.scene import sensors as sens

class TestSpectralBands(unittest.TestCase):

    def test(self):
        return sens.SpectralBands(51,"")

if __name__ == '__main__':
    unittest.main()