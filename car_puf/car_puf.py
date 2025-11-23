import sys
import os
import numpy as np

# Add project root to path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.sram_based_puf import SRAM_PUF
from model.ecc.ecc import BCHECC


class CarPUF:
    """Automotive-Grade SRAM PUF Simulator.

    This class extends the standard SRAM PUF to meet automotive reliability
    and safety standards (similar to ISO 26262 requirements). It enforces:
    - High-temperature burn-in for enrollment (Unstable Cell Masking).
    - Strong ECC (BCH) by default.
    - Lifecycle management (aging simulation).
    - Health monitoring (BIST-like features).
    """

    def __init__(self, num_cells, ecc_t=10, burn_in_rounds=20,
                 burn_in_temperature=125, burn_in_voltage_ratio=1.2):
        """Initialize the Automotive PUF.

        Args:
            num_cells (int): Total raw cells.
            ecc_t (int): Number of correctable errors bits (BCH).
                         Automotive typically needs robust correction (e.g., t=10 or more).
            burn_in_rounds (int): Number of rounds for enrollment stress test.
                                  Defaults to 20 (strict).
            burn_in_temperature (float): Stress temp. Defaults to 125°C (Auto Grade 1).
            burn_in_voltage_ratio (float): Stress voltage. Defaults to 1.2 (20% over).
        """

        # 1. Initialize the core WITHOUT ECC first.
        # We need to perform masking to see how many stable cells survive.
        self.puf_core = SRAM_PUF(
            num_cells=num_cells,
            ecc=None, # Defer ECC initialization
            burn_in_rounds=burn_in_rounds,
            burn_in_temperature=burn_in_temperature,
            burn_in_voltage_ratio=burn_in_voltage_ratio
        )

        self.enrolled = True
        self.current_age_hours = 0

        # 2. Determine available stable bits
        stable_bits_count = len(self.puf_core.puf_response)

        # If too few bits survived, we might not be able to support the requested ECC t
        # But we will try to initialize ECC with what we have.
        if stable_bits_count == 0:
             raise RuntimeError("CarPUF Initialization Failed: No stable cells survived burn-in!")

        # 3. Initialize ECC with the EXACT number of stable bits
        try:
            self.ecc_engine = BCHECC(data_len=stable_bits_count, t=ecc_t)
        except ValueError as e:
            # If t is too high for the data length (e.g. data=30, t=10 => need many parity bits),
            # this might fail or produce a huge m.
            # We try to fallback to a smaller t if strictly necessary, but for now let's raise.
            raise RuntimeError(f"CarPUF ECC Init Failed (Available Bits: {stable_bits_count}): {e}")

        # 4. Attach ECC to the core and generate helper data
        self.puf_core.ecc = self.ecc_engine
        self.puf_core.helper_data = self.ecc_engine.generate_helper_data(self.puf_core.puf_response)

        # Store Golden Key (Corrected/Original value of stable bits)
        self.golden_response = self.puf_core.puf_response

    def get_response(self, temperature=25, voltage_ratio=1.0):
        """Get the corrected PUF key under specific conditions.

        Args:
            temperature (float): Operating temperature (-40 to 150).
            voltage_ratio (float): Operating voltage noise.

        Returns:
            np.ndarray: The corrected key.
        """
        # Automotive Grade 1: -40 to 125. Grade 0: -40 to 150.
        # We allow simulation of any range.
        return self.puf_core.get_response(
            temperature=temperature,
            voltage_ratio=voltage_ratio,
            anti_aging=True # Automotive always uses anti-aging if possible
        )

    def simulate_aging(self, hours, temperature_profile=85):
        """Simulate aging of the device (e.g. 10 years at 85C).

        This updates the internal state of every cell in the array.

        Args:
            hours (int): Hours of operation.
            temperature_profile (float): Average operating temperature in Celsius.
        """
        self.current_age_hours += hours

        # Map hours to power-up cycles for the model, weighted by temperature.
        # Arrhenius equation implies exponential acceleration with temperature.
        # We use a simplified multiplier: roughly 2x aging for every 10C increase above 25C?
        # Or just a linear scaling for this simulation model.
        # Let's use a factor: (temp + 273) / (25 + 273) as a baseline multiplier,
        # but Arrhenius is stronger. Let's use: factor = 2 ^ ((temp - 25) / 10).
        # Example: 85C -> delta 60 -> 2^6 = 64x faster aging than room temp.
        # This might be too aggressive for the simple model, let's scale it down slightly.

        aging_factor = 2.0 ** ((temperature_profile - 25) / 20.0)
        effective_cycles = int(hours * aging_factor)

        # Apply aging to all cells
        for cell in self.puf_core.sram.cells:
            # We artificially increase the 'age' counter
            cell.age += effective_cycles

            # We also verify if we need to apply specific stress patterns
            # but cell.power_up handles the math based on 'age'.
            # We just need to ensure the 'age' attribute reflects time passed.
            pass

    def check_health(self):
        """Perform a Built-In Self-Test (BIST) / Health Check.

        Returns:
            dict: Health status report containing 'ber', 'health_status', 'passed'.
        """
        # Generate a response at nominal conditions to check against golden
        # In a real car, this happens at Key-On.
        current_raw = self.puf_core.sram.power_up_array(temperature=25, voltage_ratio=1.0)

        if self.puf_core.stable_mask is not None:
            current_masked = current_raw[self.puf_core.stable_mask]
        else:
            current_masked = current_raw

        # Calculate Bit Error Rate against the internal golden response
        # (Note: Golden response is already masked)
        errors = np.sum(current_masked != self.golden_response)
        ber = errors / len(self.golden_response)

        # Thresholds
        warning_threshold = 0.10 # 10% BER is getting dangerous
        failure_threshold = 0.25 # 25% might exceed ECC capacity

        status = "OK"
        passed = True

        if ber > warning_threshold:
            status = "WARNING"
        if ber > failure_threshold:
            status = "CRITICAL_FAILURE"
            passed = False

        return {
            "ber": ber,
            "errors": int(errors),
            "status": status,
            "passed": passed,
            "age_hours": self.current_age_hours
        }
