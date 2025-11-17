from model.sram import SRAM
import numpy as np

# Hamming code implementation from GeeksForGeeks
# https://www.geeksforgeeks.org/hamming-code-implementation-in-python/

def calc_redundant_bits(m):
    for i in range(m):
        if 2**i >= m + i + 1:
            return i

def pos_redundant_bits(data, r):
    j = 0
    k = 1
    m = len(data)
    res = ''
    for i in range(1, m + r + 1):
        if i == 2**j:
            res += '0'
            j += 1
        else:
            res += data[-1 * k]
            k += 1
    return res[::-1]

def calc_parity_bits(arr, r):
    n = len(arr)
    for i in range(r):
        val = 0
        for j in range(1, n + 1):
            if j & (2**i) == (2**i):
                val = val ^ int(arr[-1 * j])
        arr = arr[:n - (2**i)] + str(val) + arr[n - (2**i) + 1:]
    return arr

def detect_error(arr, nr):
    n = len(arr)
    res = 0
    for i in range(nr):
        val = 0
        for j in range(1, n + 1):
            if j & (2**i) == (2**i):
                val = val ^ int(arr[-1 * j])
        res += val * (10**i)
    return int(str(res), 2)

class SRAM_PUF:
    """
    A model of an SRAM-based PUF with ECC.
    """
    def __init__(self, rows, cols, ecc_len=None):
        """
        Initializes the SRAM-based PUF.

        Args:
            rows (int): The number of rows in the SRAM array.
            cols (int): The number of columns in the SRAM array.
            ecc_len (int, optional): The length of the ECC code. Defaults to a calculated value.
        """
        self.sram = SRAM(rows, cols)
        self.puf_response = self.sram.read().flatten()

        # Convert to string for Hamming code implementation
        puf_str = "".join(map(str, self.puf_response))

        if ecc_len is None:
            self.r = calc_redundant_bits(len(puf_str))
        else:
            self.r = ecc_len

        # Generate helper data (parity bits)
        arr = pos_redundant_bits(puf_str, self.r)
        self.helper_data = calc_parity_bits(arr, self.r)

    def get_response(self, aging_factor=0.01):
        """
        Powers up the SRAM, applies ECC, and returns the corrected PUF response.

        Args:
            aging_factor (float): The aging factor to apply to the SRAM cells.

        Returns:
            np.ndarray: The corrected PUF response.
        """
        self.sram.power_up(aging_factor)
        noisy_puf = self.sram.read().flatten()
        noisy_puf_str = "".join(map(str, noisy_puf))

        # Create a codeword from the noisy data to find the error
        arr = pos_redundant_bits(noisy_puf_str, self.r)
        arr = calc_parity_bits(arr, self.r)

        # Detect the error position
        error_pos = detect_error(arr, self.r)

        # If an error is detected, correct it in the codeword
        if error_pos != 0:
            arr_list = list(arr)
            # The error position is 1-indexed from the right
            correction_index = len(arr_list) - error_pos
            if correction_index >= 0 and correction_index < len(arr_list):
                arr_list[correction_index] = str(1 - int(arr_list[correction_index]))
                arr = "".join(arr_list)

        # Extract the original data bits from the corrected codeword
        corrected_data = ""
        for i in range(1, len(arr) + 1):
            # Check if i is a power of 2
            is_power_of_two = (i > 0) and ((i & (i - 1)) == 0)
            if not is_power_of_two:
                # Positions are 1-indexed from the left, string index is i-1
                corrected_data += arr[i-1]

        return np.array(list(map(int, list(corrected_data))))
