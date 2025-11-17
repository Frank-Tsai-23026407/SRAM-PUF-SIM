import numpy as np

class SRAMCell:
    """A model of a single Static Random-Access Memory (SRAM) cell.

    This class simulates the behavior of an SRAM cell, including its initial
    value, power-up behavior with a potential for aging-induced bit flips,
    and basic read/write operations.

    Attributes:
        initial_value (int): The stable, preferred startup value (0 or 1) of the cell.
        value (int): The current value of the cell.
    """
    def __init__(self, initial_value=None):
        """Initializes the SRAM cell.

        Args:
            initial_value (int, optional): The built-in initial value (0 or 1).
                                           If None, a random value is chosen to
                                           simulate manufacturing variations.
                                           Defaults to None.
        """
        if initial_value is None:
            self.initial_value = np.random.randint(2)
        else:
            self.initial_value = initial_value
        self.value = self.initial_value

    def power_up(self, aging_factor=0.01):
        """Simulates the power-up of the cell, considering an aging factor.

        The aging factor represents the probability of the cell's value flipping
        from its initial, preferred state upon power-up. This can be used to
        model device degradation over time.

        Args:
            aging_factor (float): The probability (from 0.0 to 1.0) of a bit flip
                                  occurring during power-up. Defaults to 0.01.
        """
        if np.random.rand() < aging_factor:
            self.value = 1 - self.initial_value
        else:
            self.value = self.initial_value

    def read(self):
        """Reads the current value of the cell.

        Returns:
            int: The current value of the cell (0 or 1).
        """
        return self.value

    def write(self, value):
        """Writes a new value to the cell.

        Args:
            value (int): The new value to write (must be 0 or 1).

        Raises:
            ValueError: If the provided value is not 0 or 1.
        """
        if value in [0, 1]:
            self.value = value
        else:
            raise ValueError("Value must be 0 or 1")
