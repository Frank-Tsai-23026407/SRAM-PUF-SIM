import numpy as np


class SRAMCell:
    """Improved SRAM cell model considering cell-specific stability parameters.

    This model simulates realistic SRAM behavior by incorporating:
    - Individual cell stability variations (threshold voltage mismatch).
    - NBTI (Negative Bias Temperature Instability) aging effects.
    - Anti-aging mitigation strategies.
    - Environmental factors (temperature, voltage).
    """

    def __init__(self, initial_value=None, stability_param=None):
        """Initialize an improved SRAM cell.

        Args:
            initial_value (int, optional): The cell's preferred power-up value (0 or 1).
                If None, it is randomly chosen to simulate manufacturing variation.
            stability_param (float, optional): Cell stability parameter representing Vth mismatch.
                Range 0-1, where 1 is most stable. If None, it is sampled from a realistic
                beta distribution.
        """
        # Determine the cell's preferred power-up value
        if initial_value is None:
            self.initial_value = np.random.randint(2)
        else:
            self.initial_value = initial_value

        # Set cell stability parameter reflecting process variations
        if stability_param is None:
            # Use beta distribution to model real threshold voltage mismatch distribution
            # Most cells are stable (close to 1), few cells are unstable (close to 0)
            self.stability = np.random.beta(a=8, b=2)
        else:
            self.stability = np.clip(stability_param, 0.0, 1.0)

        # Initialize cell value and aging counter
        self.value = self.initial_value
        self.age = 0  # Tracks cumulative aging in power-up cycles

    def power_up(self, temperature=25, voltage_ratio=1.0,
                 anti_aging=False, storage_pattern='static'):
        """Simulate the power-up behavior of the cell, considering multiple degradation mechanisms.

        This method updates the internal state of the cell (value and age) based on the
        provided environmental conditions and aging factors.

        Args:
            temperature (float): Ambient temperature in Celsius. Affects noise and aging rate.
                Default is 25°C (room temperature).
            voltage_ratio (float): Supply voltage ratio relative to nominal voltage.
                1.0 = nominal, 1.2 = 20% overvoltage (accelerated aging test).
            anti_aging (bool): Whether anti-aging mitigation is applied.
                If True, stores the inverse of initial value to counteract NBTI.
            storage_pattern (str): Storage strategy - 'static' (fixed value),
                'random' (random 0/1), or 'optimized' (anti-aging).

        Returns:
            None
        """
        # Calculate permanent NBTI damage (irreversible component, ~20-40% of total)
        # Follows sqrt(time) relationship: permanent damage = A * sqrt(time)
        permanent_aging = 0.03 * np.sqrt(self.age / 1000)

        if storage_pattern == 'optimized' or anti_aging:
            # Anti-aging strategy: Store the inverse value
            # This makes the other PMOS experience negative bias
            # Recoverable NBTI damage increases threshold voltage difference
            # Result: Cell becomes MORE stable over time
            recoverable_effect = 0.05 * np.sqrt(self.age / 1000)
            effective_stability = min(1.0, self.stability + recoverable_effect - permanent_aging)

        elif storage_pattern == 'random':
            # Random storage between 0 and 1
            # Recoverable NBTI components average out between two transistors
            # However, HCI (Hot Carrier Injection) damage increases due to frequent switching
            hci_damage = 0.02 * np.sqrt(self.age / 1000)
            effective_stability = max(0.0, self.stability - permanent_aging - hci_damage)

        else:  # storage_pattern == 'static'
            # Traditional approach: Store the natural preferred value
            # One PMOS experiences sustained negative bias
            # Both permanent and recoverable NBTI components degrade stability
            recoverable_aging = 0.07 * np.sqrt(self.age / 1000)
            effective_stability = max(0.0, self.stability - permanent_aging - recoverable_aging)

        # Environmental factors degrade the EFFECTIVE stability
        # Higher temperature reduces noise margin (reduces effective Vth difference)
        temp_degradation = abs(temperature - 25) / 500.0  # Normalized impact
        
        # Higher voltage stress degrades oxide, reducing stability
        voltage_degradation = abs(voltage_ratio - 1.0) * 0.3
        
        # Calculate final effective stability considering all factors
        effective_stability = effective_stability - temp_degradation - voltage_degradation
        effective_stability = np.clip(effective_stability, 0.0, 1.0)
        
        # Now calculate flip probability
        # This naturally caps at 50% when effective_stability = 0
        base_flip_prob = (1 - effective_stability) * 0.5
        flip_prob = base_flip_prob  # No additional multiplication!
        
        # Determine power-up value
        if np.random.rand() < flip_prob:
            self.value = 1 - self.initial_value
        else:
            self.value = self.initial_value

        # Increment age counter (number of power-up cycles experienced)
        self.age += 1

    def read(self):
        """Read the current value stored in the cell.

        Returns:
            int: Current cell value (0 or 1).
        """
        return self.value

    def write(self, value):
        """Write a new value to the cell.

        Args:
            value (int): Value to write (must be 0 or 1).

        Raises:
            ValueError: If value is not 0 or 1.

        Returns:
            None
        """
        if value in [0, 1]:
            self.value = value
        else:
            raise ValueError("Value must be 0 or 1")
