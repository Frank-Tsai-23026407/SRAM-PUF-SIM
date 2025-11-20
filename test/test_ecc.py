import unittest
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.ecc.ecc import ECC, HammingECC, BCHECC

class TestECCBase(unittest.TestCase):
    def test_not_implemented(self):
        """Test that base class methods raise NotImplementedError."""
        ecc = ECC()
        with self.assertRaises(NotImplementedError):
            ecc.generate_helper_data(np.array([1]))
        with self.assertRaises(NotImplementedError):
            ecc.correct_data(np.array([1]), None)


class TestHammingECC(unittest.TestCase):
    def test_initialization(self):
        """Test HammingECC initialization."""
        ecc = HammingECC(data_len=4)
        # For 4 bits data, we need 3 parity bits (d=4, m=4, 2^r >= m+r+1 => 2^3=8 >= 4+3+1=8)
        self.assertEqual(ecc.r, 3)

    def test_single_bit_correction(self):
        """Test correction of single bit error."""
        data_len = 16
        ecc = HammingECC(data_len)

        # Test pattern
        original_data = np.array([1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0])
        helper_data = ecc.generate_helper_data(original_data)

        # Flip one bit
        noisy_data = original_data.copy()
        noisy_data[5] = 1 - noisy_data[5]

        corrected = ecc.correct_data(noisy_data, helper_data)
        np.testing.assert_array_equal(corrected, original_data)

    def test_no_error(self):
        """Test correction when there are no errors."""
        data_len = 8
        ecc = HammingECC(data_len)
        original_data = np.array([1, 1, 0, 0, 1, 0, 1, 0])
        helper_data = ecc.generate_helper_data(original_data)

        corrected = ecc.correct_data(original_data, helper_data)
        np.testing.assert_array_equal(corrected, original_data)


class TestBCHECC(unittest.TestCase):
    def test_initialization_auto_m(self):
        """Test initialization calculating 'm' automatically."""
        # data_len = 16. needs m=5 because 2^4-1 = 15 < 16. 2^5-1 = 31 >= 16.
        ecc = BCHECC(data_len=16, t=1)
        self.assertEqual(ecc.m, 5)
        self.assertEqual(ecc.t, 1)

    def test_initialization_explicit_m(self):
        """Test initialization with explicit 'm'."""
        ecc = BCHECC(data_len=16, t=1, m=6)
        self.assertEqual(ecc.m, 6)

    def test_initialization_invalid_params(self):
        """Test initialization with invalid BCH parameters."""
        # t is too large for m=4 (n=15). 15 bits total.
        # If t=10, we need 10*4 = 40 bits parity?
        # bchlib throws RuntimeError if parameters are impossible.
        with self.assertRaises(ValueError):
            BCHECC(data_len=16, t=100, m=5)

    def test_data_too_long(self):
        """Test error when data length exceeds capacity."""
        # m=4 -> n=15. t=1 -> ecc_bits=4. max_data = 11 bits.
        # data_len = 12 should fail.
        with self.assertRaises(ValueError):
            BCHECC(data_len=12, t=1, m=4)

    def test_correction_within_limit(self):
        """Test correcting errors up to 't'."""
        data_len = 64
        t = 5
        ecc = BCHECC(data_len=data_len, t=t)

        # Generate random data
        original_data = np.random.randint(2, size=data_len)
        helper_data = ecc.generate_helper_data(original_data)

        # Introduce t errors
        noisy_data = original_data.copy()
        indices = np.random.choice(data_len, t, replace=False)
        for idx in indices:
            noisy_data[idx] = 1 - noisy_data[idx]

        corrected = ecc.correct_data(noisy_data, helper_data)
        np.testing.assert_array_equal(corrected, original_data)

    def test_correction_exceed_limit(self):
        """Test that exceeding 't' errors likely results in failure or uncorrected data."""
        # Note: Sometimes it might "correct" to a wrong codeword, but definitely won't be original
        data_len = 64
        t = 2
        ecc = BCHECC(data_len=data_len, t=t)

        original_data = np.random.randint(2, size=data_len)
        helper_data = ecc.generate_helper_data(original_data)

        # Introduce t+2 errors
        noisy_data = original_data.copy()
        indices = np.random.choice(data_len, t+2, replace=False)
        for idx in indices:
            noisy_data[idx] = 1 - noisy_data[idx]

        corrected = ecc.correct_data(noisy_data, helper_data)
        # It shouldn't match original
        self.assertFalse(np.array_equal(corrected, original_data))

    def test_input_length_validation(self):
        """Test validation of input length in generate/correct."""
        ecc = BCHECC(data_len=16, t=1)

        with self.assertRaises(ValueError):
            ecc.generate_helper_data(np.zeros(15, dtype=int))

        with self.assertRaises(ValueError):
            ecc.correct_data(np.zeros(17, dtype=int), b'')

if __name__ == '__main__':
    unittest.main()
