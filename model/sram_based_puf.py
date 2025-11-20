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

    def __init__(self, num_cells, ecc=None):
        """Initializes the SRAM_PUF.

        Args:
            num_cells (int): The number of cells in the SRAM array.
            ecc (ECC, optional): The ECC implementation to use. If None,
                                 no ECC is used. Defaults to None.
        """
        self.sram = SRAMArray(num_cells)
        # Generate the initial, "golden" response at nominal conditions
        puf_response = self.sram.power_up_array(temperature=25, voltage_ratio=1.0)
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

        if self.ecc:
            return self.ecc.correct_data(noisy_puf, self.helper_data)
        else:
            return noisy_puf
