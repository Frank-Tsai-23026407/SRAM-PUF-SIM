import sys
import os
import numpy as np

# Add project root to path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.sram import SRAMArray
from model.ecc.ecc import HammingECC


class SRAM_PUF:
    def __init__(self, num_cells, ecc=None, burn_in_rounds=0, 
                 burn_in_temperature=125, burn_in_voltage_ratio=1.2, 
                 stability_param=None):
        """
        Args:
            burn_in_rounds (int): Number of rounds for burn in phase to identify 
                                   stable cells. 0 = disabled.
            burn_in_temperature (float): Temperature in Celsius for burn in 
                                          (default: 125°C for burn-in)
            burn_in_voltage_ratio (float): Voltage ratio for burn in 
                                            (default: 1.2 = 20% overvoltage)
        """
        self.sram = SRAMArray(num_cells, stability_param=stability_param)
        self.stable_mask = None

        # Enrollment phase: generate golden response at nominal conditions
        # We generate this FIRST to check consistency during burn-in
        puf_response = self.sram.power_up_array(temperature=25, voltage_ratio=1.0)

        # burn in phase (also known as characterization or burn-in testing)
        if burn_in_rounds > 0:
            responses = []
            for _ in range(burn_in_rounds):
                # Use elevated temperature and voltage for accelerated aging
                responses.append(
                    self.sram.power_up_array(
                        temperature=burn_in_temperature,
                        voltage_ratio=burn_in_voltage_ratio
                    )
                )

            responses = np.array(responses)
            col_sums = np.sum(responses, axis=0)
            
            # Check 1: Stability at stress (must be all 0s or all 1s)
            stable_at_stress = (col_sums == 0) | (col_sums == burn_in_rounds)
            
            # Check 2: Consistency with nominal (Value at stress == Value at nominal)
            # If col_sums == 0, value is 0. Must match puf_response == 0.
            # If col_sums == rounds, value is 1. Must match puf_response == 1.
            # We can check this by comparing the "average" response at stress with nominal
            # Since we only keep stable ones, average is exactly 0 or 1.
            stress_values = (col_sums == burn_in_rounds).astype(int)
            consistent_with_nominal = (stress_values == puf_response)
            
            self.stable_mask = stable_at_stress & consistent_with_nominal
        
        if self.stable_mask is not None:
            puf_response = puf_response[self.stable_mask]

        self.ecc = ecc
        if self.ecc:
            self.helper_data = self.ecc.generate_helper_data(puf_response)
        else:
            self.helper_data = None

        self.puf_response = puf_response

    def get_response(self, temperature=25, voltage_ratio=1.0, anti_aging=False, storage_pattern='static'):
        """Generates a PUF response, simulating environmental effects and applying ECC.

        This method powers up the SRAM under the specified conditions, reads the
        (potentially noisy) response, and then applies ECC if it is enabled.

        Args:
            temperature (float): The ambient temperature in Celsius. Defaults to 25.
            voltage_ratio (float): The supply voltage ratio relative to nominal. Defaults to 1.0.
            anti_aging (bool): Whether to apply an anti-aging strategy. Defaults to False.
            storage_pattern (str): Storage strategy - 'static', 'random', or 'optimized'.
                Defaults to 'static'.

        Returns:
            np.ndarray: The PUF response as a 1D NumPy array. If ECC is enabled,
                this is the corrected response. Otherwise, it is the raw noisy response.
        """
        # Generate a new response under the given conditions
        noisy_puf = self.sram.power_up_array(
            temperature=temperature,
            voltage_ratio=voltage_ratio,
            anti_aging=anti_aging,
            storage_pattern=storage_pattern
        )

        # Apply mask if it exists
        if self.stable_mask is not None:
            noisy_puf = noisy_puf[self.stable_mask]

        if self.ecc:
            return self.ecc.correct_data(noisy_puf, self.helper_data)
        else:
            return noisy_puf
