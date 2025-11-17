from model.cell import SRAMCell
import numpy as np

class SRAM:
    """
    A model of an SRAM array.
    """
    def __init__(self, rows, cols):
        """
        Initializes the SRAM array.

        Args:
            rows (int): The number of rows in the SRAM array.
            cols (int): The number of columns in the SRAM array.
        """
        self.rows = rows
        self.cols = cols
        self.cells = np.array([[SRAMCell() for _ in range(cols)] for _ in range(rows)])

    def power_up(self, aging_factor=0.01):
        """
        Simulates the power-up of the entire SRAM array.
        """
        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i, j].power_up(aging_factor)

    def read(self):
        """
        Reads the values of all cells in the SRAM array.

        Returns:
            np.ndarray: A 2D NumPy array of the cell values.
        """
        return np.array([[self.cells[i, j].read() for j in range(self.cols)] for i in range(self.rows)])
