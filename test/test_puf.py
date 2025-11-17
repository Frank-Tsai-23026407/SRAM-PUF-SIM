import numpy as np
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.sram_based_puf import HammingECC

def test_single_bit_correction():
    """
    Tests the HammingECC's ability to correct a single-bit error.
    """
    data_len = 16
    ecc = HammingECC(data_len)

    # 1. Gnerate original data and helper data
    original_data = np.random.randint(2, size=data_len)
    original_data_str = "".join(map(str, original_data))
    helper_data = ecc.generate_helper_data(original_data_str)

    # 2. Introduce a single-bit error
    error_position = np.random.randint(data_len)
    noisy_data = np.copy(original_data)
    noisy_data[error_position] = 1 - noisy_data[error_position]
    noisy_data_str = "".join(map(str, noisy_data))

    # 3. Correct the noisy data
    corrected_data = ecc.correct_data(noisy_data_str, helper_data)

    # 4. Verify the correction
    assert np.array_equal(original_data, corrected_data), "ECC failed to correct a single-bit error."

if __name__ == "__main__":
    test_single_bit_correction()
    print("ECC test passed!")
