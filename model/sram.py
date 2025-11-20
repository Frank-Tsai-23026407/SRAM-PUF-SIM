import sys
import os
import numpy as np

# Add project root to path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.cell import SRAMCell


class SRAMArray:
    """A model of a 1D array of Static Random-Access Memory (SRAM) cells.

    This class simulates a collection of SRAM cells, providing a high-level
    interface to power up the entire array and read the resulting startup values.

    Attributes:
        num_cells (int): The total number of cells in the array.
        cells (list[SRAMCell]): A list of SRAMCell objects managed by this array.
    """

    def __init__(self, num_cells, stability_param=None):
        """Initializes the SRAM array.

        Args:
            num_cells (int): The number of cells to include in the array.
            stability_param (float, optional): Global stability parameter for all cells.
                If None, individual cells will have random stability parameters based
                on a beta distribution.
        """
        self.num_cells = num_cells
        # Initialize all cells with default (random) properties or specific stability
        self.cells = [SRAMCell(stability_param=stability_param) for _ in range(num_cells)]

    def power_up_array(self, temperature=25, voltage_ratio=1.0, anti_aging=False, storage_pattern='static'):
        """Simulates the power-up of the entire SRAM array, considering environmental and aging factors.

        This method iterates through each cell and calls its `power_up` method,
        passing the specified simulation parameters. It updates the state of each cell
        in the array.

        Args:
            temperature (float): The ambient temperature in Celsius. Defaults to 25.
            voltage_ratio (float): The supply voltage ratio relative to nominal. Defaults to 1.0.
            anti_aging (bool): Whether to apply an anti-aging strategy. Defaults to False.
            storage_pattern (str): Storage strategy - 'static', 'random', or 'optimized'.
                Defaults to 'static'.

        Returns:
            np.ndarray: A 1D NumPy array containing the startup values (0 or 1)
                of all cells in the array after power-up.
        """
        for cell in self.cells:
            cell.power_up(
                temperature=temperature,
                voltage_ratio=voltage_ratio,
                anti_aging=anti_aging,
                storage_pattern=storage_pattern
            )
        return self.read()

    def read(self):
        """Reads the current values of all cells in the SRAM array.

        Returns:
            np.ndarray: A 1D NumPy array containing the current values (0 or 1)
                of all cells.
        """
        return np.array([cell.read() for cell in self.cells])
