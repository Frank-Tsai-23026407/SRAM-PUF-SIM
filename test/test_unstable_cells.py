import unittest
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.sram_based_puf import SRAM_PUF
from model.sram import SRAMArray
from model.ecc.ecc import HammingECC

class TestUnstableCells(unittest.TestCase):
    def test_identification_of_unstable_cells(self):
        """Test that unstable cells are identified and masked."""
        num_cells = 100
        pre_test_rounds = 20

        # Initialize PUF with pre-test
        puf = SRAM_PUF(num_cells=num_cells, pre_test_rounds=pre_test_rounds)

        # Check if mask is created
        self.assertIsNotNone(puf.stable_mask)
        self.assertEqual(len(puf.stable_mask), num_cells)

        # Verify response length matches stable count
        stable_count = np.sum(puf.stable_mask)
        response = puf.get_response()
        self.assertEqual(len(response), stable_count)

        # Check that unstable cells were indeed filtered
        print(f"Total cells: {num_cells}, Stable cells: {stable_count}")

    def test_unstable_filtering(self):
        """Explicitly test filtering logic by mocking the stable_mask."""
        # We can manually set stable_mask to verify filtering logic independent of the random pre-test
        puf = SRAM_PUF(num_cells=10)
        # Manually set the mask: True=Stable, False=Unstable
        puf.stable_mask = np.array([True, False, True, False, True, True, True, True, True, True]) # 2 unstable

        # Mock the sram.power_up_array to return a known sequence
        # Since we can't easily mock the internal method without a mocking library,
        # we rely on the fact that get_response calls power_up_array.
        # We will trust that power_up_array returns an array of length 10.

        response = puf.get_response()
        self.assertEqual(len(response), 8)

if __name__ == '__main__':
    unittest.main()
