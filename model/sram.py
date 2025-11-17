from model.cell import SRAMCell
import numpy as np

class SRAM:
    """A model of a Static Random-Access Memory (SRAM) array.

    This class simulates a 2D array of SRAM cells, providing methods to
    power up the entire array and read the resulting values.

    Attributes:
        rows (int): The number of rows in the SRAM array.
        cols (int): The number of columns in the SRAM array.
        cells (np.ndarray): A 2D NumPy array of SRAMCell objects.
    """
    def __init__(self, rows, cols):
        """Initializes the SRAM array.

        Args:
            rows (int): The number of rows in the SRAM array.
            cols (int): The number of columns in the SRAM array.
        """
        self.rows = rows
        self.cols = cols
        self.cells = np.array([[SRAMCell() for _ in range(cols)] for _ in range(rows)])

    def power_up(self, aging_factor=0.01):
        """Simulates the power-up of the entire SRAM array.

        This method iterates through each cell in the array and calls its
        `power_up` method, applying the specified aging factor.

        Args:
            aging_factor (float): The probability (from 0.0 to 1.0) of a bit
                                  flip occurring for each cell during
                                  power-up. Defaults to 0.01.
        """
        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i, j].power_up(aging_factor)

    def read(self):
        """Reads the values of all cells in the SRAM array.

        Returns:
            np.ndarray: A 2D NumPy array containing the current values (0 or 1)
                        of all cells in the SRAM array.
        """
        return np.array([[self.cells[i, j].read() for j in range(self.cols)] for i in range(self.rows)])
