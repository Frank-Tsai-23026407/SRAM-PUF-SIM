import numpy as np

class SRAMCell:
    """Simulates a single Static Random-Access Memory (SRAM) cell.

    This model captures the intrinsic properties of an SRAM cell, including its
    preferred startup value (initial_value) and its inherent stability. It 
    simulates the power-up process, considering environmental factors like 
    temperature and voltage, as well as aging effects (NBTI and anti-aging 
    mechanisms). The cell's state can be read and written to.

    Attributes:
        initial_value (int): The stable, preferred startup value (0 or 1) of the cell.
        stability (float): The intrinsic stability of the cell (0.0 to 1.0).
        value (int): The current value of the cell (0 or 1).
        age (int): A counter for the number of power-up cycles, simulating aging.
    """
    def __init__(self, initial_value=None, stability_param=None):
        """
        Args:
            initial_value (int, optional): The preferred startup value (0 or 1) 
                of the cell. If None, a random value is chosen. Defaults to None.
            stability_param (float, optional): A parameter representing the cell's 
                stability, analogous to Vth mismatch. A value closer to 1.0 
                indicates higher stability, while a value closer to 0.0 indicates 
                lower stability. If None, a value is sampled from a Beta 
                distribution to mimic real-world variations. Defaults to None.
        """
        # Set the initial (preferred) power-up value.
        if initial_value is None:
            self.initial_value = np.random.randint(2)
        else:
            self.initial_value = initial_value
        
        # Set the stability parameter.
        # If not provided, sample from a distribution that mimics reality.
        if stability_param is None:
            # Use a Beta distribution to simulate a realistic distribution:
            # Most cells are very stable (close to 1.0), while a few are 
            # very unstable (close to 0.0).
            self.stability = np.random.beta(a=8, b=2)  
        else:
            self.stability = np.clip(stability_param, 0.0, 1.0)
        
        self.value = self.initial_value
        self.age = 0  # Tracks the aging of the cell.

    def power_up(self, temperature=25, voltage_ratio=1.0, 
                 anti_aging=False):
        """
        Simulates the power-up behavior of the cell, considering various factors.
        
        Args:
            temperature (float): The ambient temperature in Celsius, which affects noise.
            voltage_ratio (float): The supply voltage ratio relative to the nominal voltage.
            anti_aging (bool): Whether to apply an anti-aging mitigation strategy.
        """
        # Calculate the effect of aging on stability.
        if anti_aging:
            # Anti-aging techniques can make the cell more stable over time.
            aging_effect = 0.05 * np.sqrt(self.age / 1000)  
            effective_stability = min(1.0, self.stability + aging_effect)
        else:
            # Without anti-aging, NBTI (Negative Bias Temperature Instability) degrades stability.
            aging_effect = 0.1 * np.sqrt(self.age / 1000)
            effective_stability = max(0.0, self.stability - aging_effect)
        
        # Temperature effect: Deviation from 25°C increases noise.
        temp_factor = 1.0 + abs(temperature - 25) / 100.0
        
        # Voltage effect: Deviation from the nominal voltage increases noise.
        voltage_factor = 1.0 + abs(voltage_ratio - 1.0) * 2.0
        
        # Calculate the final flip probability.
        # For a highly stable cell, the flip probability is close to 0.
        # For a highly unstable cell, the flip probability is close to 0.5.
        base_flip_prob = (1 - effective_stability) * 0.5
        flip_prob = base_flip_prob * temp_factor * voltage_factor
        
        # Determine the power-up value based on the flip probability.
        if np.random.rand() < flip_prob:
            self.value = 1 - self.initial_value  # Bit flip occurred.
        else:
            self.value = self.initial_value
        
        # Increment the age counter after each power-up cycle.
        self.age += 1  
        
    def read(self):
        return self.value
    
    def write(self, value):
        if value in [0, 1]:
            self.value = value
        else:
            raise ValueError("Value must be 0 or 1")
