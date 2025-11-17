import numpy as np

class SRAMCell:
    """
    A model of a single SRAM cell.
    """
    def __init__(self, initial_value=None):
        """
        Initializes the SRAM cell.

        Args:
            initial_value (int, optional): The built-in initial value (0 or 1).
                                           If None, a random value is chosen.
        """
        if initial_value is None:
            self.initial_value = np.random.randint(2)
        else:
            self.initial_value = initial_value
        self.value = self.initial_value

    def power_up(self, aging_factor=0.01):
        """
        Simulates the power-up of the cell, considering an aging factor.

        The aging factor represents the probability of the cell's value flipping
        from its initial state upon power-up.

        Args:
            aging_factor (float): The probability (0.0 to 1.0) of a bit flip.
        """
        if np.random.rand() < aging_factor:
            self.value = 1 - self.initial_value
        else:
            self.value = self.initial_value

    def read(self):
        """
        Reads the current value of the cell.

        Returns:
            int: The current value (0 or 1).
        """
        return self.value

    def write(self, value):
        """
        Writes a new value to the cell.

        Args:
            value (int): The new value to write (0 or 1).
        """
        if value in [0, 1]:
            self.value = value
        else:
            raise ValueError("Value must be 0 or 1")
