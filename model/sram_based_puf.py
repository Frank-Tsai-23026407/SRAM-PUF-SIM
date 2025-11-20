import sys
import os
import numpy as np

# Add project root to path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.sram import SRAMArray
from model.ecc.ecc import HammingECC


class SRAM_PUF:
    """A model of an SRAM-based PUF with optional Error Correction Code (ECC).

    This class simulates an SRAM-based Physical Unclonable Function (PUF),
    which generates a unique, device-specific response based on the startup
    behavior of an SRAM array. It can be configured with ECC to improve
    the reliability of the response.

    Attributes:
        sram (SRAMArray): The SRAM array used for the PUF.
        ecc (ECC): The ECC object used for error correction.
        helper_data (any): The helper data generated from the initial PUF
                           response required for ECC.
    """

    def __init__(self, num_cells, ecc=None, pre_test_rounds=0):
        """Initializes the SRAM_PUF.

        Args:
            num_cells (int): The number of cells in the SRAM array.
            ecc (ECC, optional): The ECC implementation to use. If None,
                                 no ECC is used. Defaults to None.
            pre_test_rounds (int, optional): The number of rounds to perform a
                                             pre-test to identify unstable cells.
                                             Defaults to 0 (disabled).
        """
        self.sram = SRAMArray(num_cells)
        self.stable_mask = None

        # Perform pre-test if requested
        if pre_test_rounds > 0:
            # Collect responses from multiple power-up cycles
            responses = []
            for _ in range(pre_test_rounds):
                responses.append(self.sram.power_up_array(temperature=25, voltage_ratio=1.0))

            responses = np.array(responses)
            # A cell is stable if it has the same value in all rounds
            # We check if the variance of each column is 0, or simply if all values are equal to the first row
            # If sum of a column is 0 (all 0s) or pre_test_rounds (all 1s), it is stable.
            col_sums = np.sum(responses, axis=0)
            self.stable_mask = (col_sums == 0) | (col_sums == pre_test_rounds)

            # Depending on the implementation, we might want to ensure we have at least some stable cells
            if np.sum(self.stable_mask) == 0:
                 # Fallback: if all are unstable (unlikely), use all cells or raise warning
                 # For now, we'll leave it empty, which might cause issues downstream but is correct behavior
                 pass

        # Generate the initial, "golden" response at nominal conditions
        puf_response = self.sram.power_up_array(temperature=25, voltage_ratio=1.0)

        # Apply mask if it exists
        if self.stable_mask is not None:
            puf_response = puf_response[self.stable_mask]

        self.ecc = ecc

        if self.ecc:
            self.helper_data = self.ecc.generate_helper_data(puf_response)
        else:
            self.helper_data = None

    def get_response(self, temperature=25, voltage_ratio=1.0, anti_aging=False):
        """
        Generates a PUF response, simulating environmental effects and applying ECC.

        This method powers up the SRAM under the specified conditions, reads the
        (potentially noisy) response, and then applies ECC if it is enabled.

        Args:
            temperature (float): The ambient temperature in Celsius.
            voltage_ratio (float): The supply voltage ratio relative to nominal.
            anti_aging (bool): Whether to apply an anti-aging strategy.

        Returns:
            np.ndarray: The PUF response as a 1D NumPy array.
        """
        # Generate a new response under the given conditions
        noisy_puf = self.sram.power_up_array(
            temperature=temperature,
            voltage_ratio=voltage_ratio,
            anti_aging=anti_aging
        )

        # Apply mask if it exists
        if self.stable_mask is not None:
            noisy_puf = noisy_puf[self.stable_mask]

        if self.ecc:
            return self.ecc.correct_data(noisy_puf, self.helper_data)
        else:
            return noisy_puf
