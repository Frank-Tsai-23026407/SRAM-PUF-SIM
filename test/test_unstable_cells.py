import unittest
import numpy as np
from model.sram_based_puf import SRAM_PUF
from model.ecc.ecc import HammingECC

class TestUnstableCells(unittest.TestCase):
    def test_pre_test_identification(self):
        # Use a small SRAM
        rows, cols = 8, 8

        # Initialize PUF with pre-test enabled
        # We use a high aging factor to provoke instability if possible,
        # but SRAMCell stability logic relies on internal stability parameter.
        # To deterministically test this, we might need to rely on the fact
        # that some cells are created with low stability.

        # However, since we can't control random seed easily inside the classes without modifying them,
        # we will just run it and check if the mask is created and applied correctly.

        puf = SRAM_PUF(rows, cols, pre_test_rounds=5, pre_test_aging_factor=0.05)

        # Check if valid_mask exists and has correct shape
        self.assertTrue(hasattr(puf, 'valid_mask'))
        self.assertEqual(puf.valid_mask.shape, (rows, cols))

        # Check if puf_response length matches the number of True values in mask
        expected_len = np.sum(puf.valid_mask)
        self.assertEqual(len(puf.puf_response), expected_len)

        # Ensure puf_response is not empty (statistically unlikely all are unstable)
        self.assertGreater(len(puf.puf_response), 0)

        # Test get_response returns same length
        response = puf.get_response()
        self.assertEqual(len(response), expected_len)

    def test_no_pre_test(self):
        rows, cols = 8, 8
        puf = SRAM_PUF(rows, cols, pre_test_rounds=0)

        # Mask should be all ones
        self.assertTrue(np.all(puf.valid_mask))
        self.assertEqual(len(puf.puf_response), rows * cols)

    def test_unstable_filtering(self):
        # We will manually force some cells to be unstable by mocking or accessing internals
        rows, cols = 4, 4
        puf = SRAM_PUF(rows, cols, pre_test_rounds=0) # No pre-test initially to setup

        # We can't easily force instability on existing puf without modifying cells.
        # But we can verify that IF mask is set, logic works.

        # Manually set mask
        puf.valid_mask = np.ones((rows, cols), dtype=bool)
        puf.valid_mask[0, 0] = False # Mark (0,0) as unstable

        # Total cells = 16. Masked 1. Expected 15.

        # Update puf_response manually to reflect what would happen
        # (In real usage, this happens in init)
        puf.puf_response = puf.sram.read().flatten()[puf.valid_mask.flatten()]

        self.assertEqual(len(puf.puf_response), 15)

        # get_response should also return 15
        resp = puf.get_response()
        self.assertEqual(len(resp), 15)

if __name__ == '__main__':
    unittest.main()
