import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.sram import SRAMArray
from model.cell import SRAMCell

class TestSRAMArray(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)

    def test_initialization(self):
        """Test correct initialization of SRAM array."""
        num_cells = 100
        sram = SRAMArray(num_cells)
        self.assertEqual(len(sram.cells), num_cells)
        self.assertIsInstance(sram.cells[0], SRAMCell)

    def test_read(self):
        """Test reading from the array returns numpy array."""
        num_cells = 10
        sram = SRAMArray(num_cells)
        response = sram.read()
        self.assertIsInstance(response, np.ndarray)
        self.assertEqual(len(response), num_cells)
        self.assertTrue(all(x in [0, 1] for x in response))

    def test_power_up_array_defaults(self):
        """Test power_up_array with default parameters."""
        num_cells = 10
        sram = SRAMArray(num_cells)

        # Use a spy to verify cells are powered up
        with patch.object(SRAMCell, 'power_up', wraps=sram.cells[0].power_up) as mock_power_up:
             # We only mock the first cell's power_up method for verification or loop through all
             # Since we can't easily wrap all existing instances without iterating
             pass

        response = sram.power_up_array()
        self.assertEqual(len(response), num_cells)
        # Check that all cells have age incremented (power_up was called)
        for cell in sram.cells:
            self.assertEqual(cell.age, 1)

    def test_power_up_array_parameters(self):
        """Test power_up_array passes parameters to cells."""
        num_cells = 5
        sram = SRAMArray(num_cells)

        # Mock the power_up method on the class to verify calls
        with patch('model.cell.SRAMCell.power_up') as mock_power_up:
            sram.power_up_array(temperature=50, voltage_ratio=1.1, anti_aging=True)

            self.assertEqual(mock_power_up.call_count, num_cells)
            mock_power_up.assert_called_with(
                temperature=50,
                voltage_ratio=1.1,
                anti_aging=True
            )

    def test_large_array_init(self):
        """Test initialization of a larger array (smoke test)."""
        num_cells = 10000
        sram = SRAMArray(num_cells)
        self.assertEqual(len(sram.cells), num_cells)

if __name__ == '__main__':
    unittest.main()
