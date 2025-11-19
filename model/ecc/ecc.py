import numpy as np
import bchlib

class ECC:
    """Base class for Error Correction Code implementations."""

    def generate_helper_data(self, data):
        """Generates helper data for the given data.

        Args:
            data (np.ndarray): The input data.

        Returns:
            The helper data.
        """
        raise NotImplementedError

    def correct_data(self, noisy_data, helper_data):
        """Corrects errors in the noisy data using the helper data.

        Args:
            noisy_data (np.ndarray): The noisy data.
            helper_data: The helper data.

        Returns:
            np.ndarray: The corrected data.
        """
        raise NotImplementedError


class HammingECC(ECC):
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

    def generate_helper_data(self, data):
        """Generates the helper data (parity bits) for the given data.

        Args:
            data (np.ndarray): The input data.

        Returns:
            str: The parity bits.
        """
        data_str = "".join(map(str, data))
        arr = self._pos_redundant_bits(data_str, self.r)
        codeword = self._calc_parity_bits(arr, self.r)

        parity_bits = ""
        for i in range(self.r):
            p_pos = 2**i
            p_idx = len(codeword) - p_pos
            parity_bits += codeword[p_idx]
        return parity_bits

    def correct_data(self, noisy_data, helper_data):
        """Corrects a single-bit error in the noisy data.

        Args:
            noisy_data (np.ndarray): The noisy data string.
            helper_data (str): The parity bits.

        Returns:
            np.ndarray: The corrected data as a NumPy array of integers.
        """
        noisy_data_str = "".join(map(str, noisy_data))
        arr = self._pos_redundant_bits(noisy_data_str, self.r)

        # We don't know the parity bits of the noisy data, so we calculate them
        codeword_noisy_data = self._calc_parity_bits(arr, self.r)

        # Reconstruct the codeword with the original parity bits to find the error
        received_codeword_list = list(codeword_noisy_data)
        for i in range(self.r):
            p_pos = 2**i
            p_idx = len(received_codeword_list) - p_pos
            if 0 <= p_idx < len(received_codeword_list):
                 received_codeword_list[p_idx] = helper_data[i]

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


class BCHECC(ECC):
    """BCH Error Correction Code implementation."""

    def __init__(self, data_len, t=5):
        """Initializes the BCHECC class.
        Args:
            data_len (int): The length of the data string (number of bits).
            t (int): The error correction capability in bits.
        """
        m = 1
        while (2**m)-1 < data_len:
            m += 1
        self.bch = bchlib.BCH(t=t, m=m)
        self.data_len = data_len

    def generate_helper_data(self, data):
        """Generates helper data for the given data.
        Args:
            data (np.ndarray): The input data.
        Returns:
            bytes: The ECC data.
        """
        data_bytes = np.packbits(data).tobytes()
        ecc = self.bch.encode(data_bytes)
        return ecc

    def correct_data(self, noisy_data, helper_data):
        """Corrects errors in the noisy data using the helper data.
        Args:
            noisy_data (np.ndarray): The noisy data.
            helper_data (bytes): The ECC data.
        Returns:
            np.ndarray: The corrected data.
        """
        data_bytes = bytearray(np.packbits(noisy_data).tobytes())
        ecc_bytes = bytearray(helper_data)

        bitflips = self.bch.decode(data_bytes, ecc_bytes)

        if bitflips != -1:
            self.bch.correct(data_bytes, ecc_bytes)

        corrected_bits = np.unpackbits(np.frombuffer(data_bytes, dtype=np.uint8))
        return corrected_bits[:self.data_len]
