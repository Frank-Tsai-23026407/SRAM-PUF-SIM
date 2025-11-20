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
        valid_mask (np.ndarray): A boolean mask indicating stable cells.
    """

    def __init__(self, rows, cols, ecc=None, pre_test_rounds=0, pre_test_aging_factor=0.01):
        """Initializes the SRAM_PUF.

        Args:
            rows (int): The number of rows in the SRAM array.
            cols (int): The number of columns in the SRAM array.
            ecc (ECC, optional): The ECC implementation to use. If None,
                                 no ECC is used. Defaults to None.
            pre_test_rounds (int, optional): Number of power-up cycles to run
                                             to identify unstable cells.
                                             Defaults to 0 (disabled).
            pre_test_aging_factor (float, optional): Aging factor used during
                                                     pre-test. Defaults to 0.01.
        """
        self.sram = SRAM(rows, cols)

        # Capture the ideal response (based on initial_value)
        raw_response = self.sram.read()

        self.valid_mask = np.ones((rows, cols), dtype=bool)

        if pre_test_rounds > 0:
            self.valid_mask = self._identify_unstable_cells(pre_test_rounds, pre_test_aging_factor)

        # Filter the response to include only stable cells
        self.puf_response = raw_response.flatten()[self.valid_mask.flatten()]

        self.ecc = ecc

        if self.ecc:
            # Note: The ecc object must be compatible with the length of self.puf_response
            # if pre-test is used.
            try:
                self.helper_data = self.ecc.generate_helper_data(self.puf_response)
            except Exception as e:
                # If ECC fails (e.g. due to length mismatch), we warn but proceed
                print(f"Warning: ECC generation failed: {e}")
                self.helper_data = None
        else:
            self.helper_data = None

    def _identify_unstable_cells(self, rounds, aging_factor):
        """Identifies unstable cells by powering up multiple times.

        Args:
            rounds (int): Number of rounds to test.
            aging_factor (float): Aging factor to use.

        Returns:
            np.ndarray: A boolean mask (True for stable, False for unstable).
        """
        accumulated_values = np.zeros((self.sram.rows, self.sram.cols), dtype=int)

        for _ in range(rounds):
            self.sram.power_up(aging_factor)
            accumulated_values += self.sram.read()

        # A stable cell should be consistently 0 or consistently 1
        # So sum should be 0 or 'rounds'
        stable_mask = (accumulated_values == 0) | (accumulated_values == rounds)
        return stable_mask

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

        # Apply the valid mask
        filtered_puf = noisy_puf[self.valid_mask.flatten()]

        if self.ecc and self.helper_data is not None:
            return self.ecc.correct_data(filtered_puf, self.helper_data)
        else:
            return filtered_puf
