from model.sram import SRAM
from model.ecc.ecc import HammingECC
import numpy as np

class SRAM_PUF:
    """A model of an SRAM-based PUF with Error Correction Code (ECC).

    This class simulates an SRAM-based Physical Unclonable Function (PUF),
    which generates a unique, device-specific response. It includes a Hamming
    code implementation to correct for errors that may occur due to aging.

    Attributes:
        sram (SRAM): The SRAM array used for the PUF.
        puf_response (np.ndarray): The initial, flattened response of the PUF.
        ecc (ECC): The ECC object used for error correction.
        helper_data (str): The helper data (codeword) generated from the
                           initial PUF response.
    """

    def __init__(self, rows, cols, ecc=None):
        """Initializes the SRAM_PUF.

        Args:
            rows (int): The number of rows in the SRAM array.
            cols (int): The number of columns in the SRAM array.
            ecc (ECC, optional): The ECC implementation to use. If None,
                                 no ECC is used. Defaults to None.
        """
        self.sram = SRAM(rows, cols)
        self.puf_response = self.sram.read().flatten()
        self.ecc = ecc

        if self.ecc:
            self.helper_data = self.ecc.generate_helper_data(self.puf_response)
        else:
            self.helper_data = None

    def get_response(self, aging_factor=0.01):
        """Generates a PUF response, simulating aging and applying ECC.

        This method first powers up the SRAM with a given aging factor,
        reads the (potentially noisy) response. If ECC is enabled, it
        corrects any errors.

        Args:
            aging_factor (float): The probability (from 0.0 to 1.0) of a bit
                                  flip occurring for each cell during
                                  power-up. Defaults to 0.01.

        Returns:
            np.ndarray: The PUF response as a NumPy array.
        """
        self.sram.power_up(aging_factor)
        noisy_puf = self.sram.read().flatten()

        if self.ecc:
            return self.ecc.correct_data(noisy_puf, self.helper_data)
        else:
            return noisy_puf
