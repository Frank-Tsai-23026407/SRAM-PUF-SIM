from model.sram import SRAM
import numpy as np

class HammingECC:
    """A class to handle Hamming code error detection and correction.

    This class provides the functionality to generate helper data (parity bits)
    for a given data string and to correct single-bit errors in a noisy version
    of that data.

    Attributes:
        r (int): The number of redundant bits required for the given data length.
    """
    def __init__(self, data_len):
        """Initializes the HammingECC class.

        Args:
            data_len (int): The length of the data string (number of bits).
        """
        self.r = self._calc_redundant_bits(data_len)

    def _calc_redundant_bits(self, m):
        """Calculates the number of redundant bits required.

        This method finds the smallest `r` such that 2^r >= m + r + 1.

        Args:
            m (int): The length of the data.

        Returns:
            int: The number of redundant bits.
        """
        for i in range(m):
            if 2**i >= m + i + 1:
                return i

    def _pos_redundant_bits(self, data, r):
        """Positions the redundant bits in the data string.

        This method inserts placeholders for the redundant bits at positions
        that are powers of 2.

        Args:
            data (str): The data string.
            r (int): The number of redundant bits.

        Returns:
            str: The data string with placeholders for redundant bits.
        """
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

    def _calc_parity_bits(self, arr, r):
        """Calculates the parity bits for the given data.

        Args:
            arr (str): The data string with placeholders for redundant bits.
            r (int): The number of redundant bits.

        Returns:
            str: The data string with the calculated parity bits.
        """
        n = len(arr)
        for i in range(r):
            val = 0
            for j in range(1, n + 1):
                if j & (2**i) == (2**i):
                    val = val ^ int(arr[-1 * j])
            arr = arr[:n - (2**i)] + str(val) + arr[n - (2**i) + 1:]
        return arr

    def generate_helper_data(self, data_str):
        """Generates the helper data (codeword) for the given data.

        Args:
            data_str (str): The input data string.

        Returns:
            str: The Hamming codeword, including parity bits.
        """
        arr = self._pos_redundant_bits(data_str, self.r)
        return self._calc_parity_bits(arr, self.r)

    def correct_data(self, noisy_data_str, helper_data):
        """Corrects a single-bit error in the noisy data.

        Args:
            noisy_data_str (str): The noisy data string.
            helper_data (str): The original helper data (codeword).

        Returns:
            np.ndarray: The corrected data as a NumPy array of integers.
        """
        arr = self._pos_redundant_bits(noisy_data_str, self.r)

        # We need to insert the original parity bits to detect the error
        received_codeword_list = list(arr)
        for i in range(self.r):
            p_pos = 2**i
            p_idx = len(received_codeword_list) - p_pos
            if 0 <= p_idx < len(received_codeword_list):
                 received_codeword_list[p_idx] = helper_data[p_idx]

        received_codeword = "".join(received_codeword_list)

        error_pos = self._detect_error(received_codeword, self.r)

        if error_pos != 0:
            arr_list = list(received_codeword)
            correction_index = len(arr_list) - error_pos
            if 0 <= correction_index < len(arr_list):
                arr_list[correction_index] = str(1 - int(arr_list[correction_index]))
            corrected_codeword = "".join(arr_list)
        else:
            corrected_codeword = received_codeword

        corrected_data_rev = ""
        for i in range(1, len(corrected_codeword) + 1):
            # Check if i is not a power of 2
            if not ((i > 0) and ((i & (i - 1)) == 0)):
                # Traverse from the right to match the bit order
                corrected_data_rev += corrected_codeword[len(corrected_codeword) - i]

        # The data is extracted in reverse, so we flip it back
        corrected_data = corrected_data_rev[::-1]
        return np.array(list(map(int, list(corrected_data))))

    def _detect_error(self, arr, nr):
        """Detects the position of a single-bit error.

        Args:
            arr (str): The received codeword.
            nr (int): The number of redundant bits.

        Returns:
            int: The position of the error bit (0 if no error).
        """
        n = len(arr)
        res = 0
        for i in range(nr):
            val = 0
            for j in range(1, n + 1):
                if j & (2**i) == (2**i):
                    val = val ^ int(arr[-1 * j])
            res = res + val * (10**i)

        # Convert binary string to integer
        return int(str(res), 2)

class SRAM_PUF:
    """A model of an SRAM-based PUF with Error Correction Code (ECC).

    This class simulates an SRAM-based Physical Unclonable Function (PUF),
    which generates a unique, device-specific response. It includes a Hamming
    code implementation to correct for errors that may occur due to aging.

    Attributes:
        sram (SRAM): The SRAM array used for the PUF.
        puf_response (np.ndarray): The initial, flattened response of the PUF.
        ecc (HammingECC): The Hamming ECC object used for error correction.
        helper_data (str): The helper data (codeword) generated from the
                           initial PUF response.
    """

    def __init__(self, rows, cols, ecc_len=None):
        """Initializes the SRAM_PUF.

        Args:
            rows (int): The number of rows in the SRAM array.
            cols (int): The number of columns in the SRAM array.
            ecc_len (int, optional): The length of the data to be used for ECC.
                                     If None, the entire PUF response is used.
                                     Defaults to None.
        """
        self.sram = SRAM(rows, cols)
        self.puf_response = self.sram.read().flatten()
        puf_str = "".join(map(str, self.puf_response))

        self.ecc = HammingECC(len(puf_str))
        self.helper_data = self.ecc.generate_helper_data(puf_str)

    def get_response(self, aging_factor=0.01):
        """Generates a PUF response, simulating aging and applying ECC.

        This method first powers up the SRAM with a given aging factor,
        reads the (potentially noisy) response, and then uses the Hamming ECC
        to correct any single-bit errors.

        Args:
            aging_factor (float): The probability (from 0.0 to 1.0) of a bit
                                  flip occurring for each cell during
                                  power-up. Defaults to 0.01.

        Returns:
            np.ndarray: The corrected PUF response as a NumPy array.
        """
        self.sram.power_up(aging_factor)
        noisy_puf = self.sram.read().flatten()
        noisy_puf_str = "".join(map(str, noisy_puf))

        return self.ecc.correct_data(noisy_puf_str, self.helper_data)
