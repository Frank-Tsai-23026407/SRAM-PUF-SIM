from model.sram import SRAM
import numpy as np

class HammingECC:
    """
    A class to handle Hamming code error correction.
    """
    def __init__(self, data_len):
        self.r = self._calc_redundant_bits(data_len)

    def _calc_redundant_bits(self, m):
        for i in range(m):
            if 2**i >= m + i + 1:
                return i

    def _pos_redundant_bits(self, data, r):
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
        n = len(arr)
        for i in range(r):
            val = 0
            for j in range(1, n + 1):
                if j & (2**i) == (2**i):
                    val = val ^ int(arr[-1 * j])
            arr = arr[:n - (2**i)] + str(val) + arr[n - (2**i) + 1:]
        return arr

    def generate_helper_data(self, data_str):
        arr = self._pos_redundant_bits(data_str, self.r)
        return self._calc_parity_bits(arr, self.r)

    def correct_data(self, noisy_data_str, helper_data):
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
    """
    A model of an SRAM-based PUF with ECC.
    """
    def __init__(self, rows, cols, ecc_len=None):
        self.sram = SRAM(rows, cols)
        self.puf_response = self.sram.read().flatten()
        puf_str = "".join(map(str, self.puf_response))

        self.ecc = HammingECC(len(puf_str))
        self.helper_data = self.ecc.generate_helper_data(puf_str)

    def get_response(self, aging_factor=0.01):
        self.sram.power_up(aging_factor)
        noisy_puf = self.sram.read().flatten()
        noisy_puf_str = "".join(map(str, noisy_puf))

        return self.ecc.correct_data(noisy_puf_str, self.helper_data)
