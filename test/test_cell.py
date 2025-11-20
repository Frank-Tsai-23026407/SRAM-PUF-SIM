import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.cell import SRAMCell

class TestSRAMCell(unittest.TestCase):
    def setUp(self):
        # Fixed seed for reproducibility in tests involving random numbers
        np.random.seed(42)

    def test_initialization_defaults(self):
        """Test initialization with default parameters."""
        cell = SRAMCell()
        self.assertIn(cell.initial_value, [0, 1])
        self.assertTrue(0 <= cell.stability <= 1)
        self.assertEqual(cell.value, cell.initial_value)
        self.assertEqual(cell.age, 0)

    def test_initialization_explicit(self):
        """Test initialization with explicit parameters."""
        cell = SRAMCell(initial_value=1, stability_param=0.8)
        self.assertEqual(cell.initial_value, 1)
        self.assertEqual(cell.stability, 0.8)
        self.assertEqual(cell.value, 1)

    def test_initialization_clipping(self):
        """Test that stability parameter is clipped to [0, 1]."""
        cell_high = SRAMCell(stability_param=1.5)
        self.assertEqual(cell_high.stability, 1.0)

        cell_low = SRAMCell(stability_param=-0.5)
        self.assertEqual(cell_low.stability, 0.0)

    def test_write_valid(self):
        """Test writing valid values."""
        cell = SRAMCell(initial_value=0)
        cell.write(1)
        self.assertEqual(cell.value, 1)
        cell.write(0)
        self.assertEqual(cell.value, 0)

    def test_write_invalid(self):
        """Test writing invalid values raises ValueError."""
        cell = SRAMCell()
        with self.assertRaises(ValueError):
            cell.write(2)
        with self.assertRaises(ValueError):
            cell.write(-1)
        with self.assertRaises(ValueError):
            cell.write("0")

    def test_read(self):
        """Test reading the value."""
        cell = SRAMCell(initial_value=1)
        self.assertEqual(cell.read(), 1)
        cell.write(0)
        self.assertEqual(cell.read(), 0)

    @patch('numpy.random.rand')
    def test_power_up_no_flip(self, mock_rand):
        """Test power_up where no flip occurs (rand > flip_prob)."""
        # Stability 1.0 -> flip_prob = 0.0. Any rand > 0 should result in no flip.
        cell = SRAMCell(initial_value=1, stability_param=1.0)
        mock_rand.return_value = 0.5 # 0.5 > 0.0

        cell.power_up()
        self.assertEqual(cell.value, 1)
        self.assertEqual(cell.age, 1)

    @patch('numpy.random.rand')
    def test_power_up_forced_flip(self, mock_rand):
        """Test power_up where flip occurs (rand < flip_prob)."""
        # Stability 0.0 -> base_flip_prob = 0.5.
        cell = SRAMCell(initial_value=1, stability_param=0.0)
        mock_rand.return_value = 0.1 # 0.1 < 0.5

        cell.power_up()
        self.assertEqual(cell.value, 0) # Flipped from 1 to 0
        self.assertEqual(cell.age, 1)

    def test_aging_increment(self):
        """Test that age increments correctly."""
        cell = SRAMCell()
        for i in range(5):
            self.assertEqual(cell.age, i)
            cell.power_up()
        self.assertEqual(cell.age, 5)

    @patch('numpy.random.rand')
    def test_temperature_effect(self, mock_rand):
        """Test that higher temperature increases flip probability logic."""
        # Ensure mock returns a float
        mock_rand.return_value = 0.5

        cell = SRAMCell(stability_param=0.5)
        # Run with high temperature
        cell.power_up(temperature=125)
        self.assertEqual(cell.age, 1)

    @patch('numpy.random.rand')
    def test_voltage_effect(self, mock_rand):
        """Test that voltage deviation logic runs."""
        # Ensure mock returns a float
        mock_rand.return_value = 0.5

        cell = SRAMCell(stability_param=0.5)
        # Run with high voltage
        cell.power_up(voltage_ratio=1.2)
        self.assertEqual(cell.age, 1)

    def test_storage_patterns(self):
        """Test that different storage patterns execute."""
        cell = SRAMCell(stability_param=0.5)

        # Static
        cell.power_up(storage_pattern='static')
        self.assertEqual(cell.age, 1)

        # Random
        cell.power_up(storage_pattern='random')
        self.assertEqual(cell.age, 2)

        # Optimized
        cell.power_up(storage_pattern='optimized')
        self.assertEqual(cell.age, 3)

    def test_anti_aging_parameter(self):
        """Test anti_aging parameter (equivalent to optimized)."""
        cell = SRAMCell(stability_param=0.5)
        cell.power_up(anti_aging=True)
        self.assertEqual(cell.age, 1)

if __name__ == '__main__':
    unittest.main()
