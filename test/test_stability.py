"""
This script evaluates the stability of the SRAM PUF model by simulating its
power-up behavior over multiple cycles. It reproduces the observation that a
large percentage of SRAM cells are stable, while a small fraction are unstable.
"""
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# Add project root to path to allow absolute imports from the model package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.sram import SRAMArray

# --- Simulation Parameters ---
# Using a smaller number for quick validation. 
# The paper uses 8,000,000, which is computationally intensive.
NUM_CELLS = 100000  # Reduced from 8,000,000 for faster execution
NUM_RUNS = 60       # Number of repeated power-up tests

def run_stability_evaluation():
    """
    Performs the SRAM PUF stability evaluation.
    """
    print(f"Initializing SRAM with {NUM_CELLS} cells...")
    sram = SRAMArray(num_cells=NUM_CELLS)

    print("Generating enrollment response at nominal conditions (25°C, 1.0V)...")
    # Get the initial, "golden" response at nominal conditions
    ref_response = sram.power_up_array(temperature=25, voltage_ratio=1.0)

    # Array to store the number of errors (flips) for each cell
    cell_error_counts = np.zeros(NUM_CELLS, dtype=int)

    print(f"Simulating {NUM_RUNS} power-up cycles to measure stability...")
    # Simulate repeated power-up tests
    for _ in tqdm(range(NUM_RUNS), desc="Simulation Progress"):
        # Get a new response under the same nominal conditions
        current_response = sram.power_up_array(temperature=25, voltage_ratio=1.0)
        
        # Find which cells flipped compared to the reference response
        errors = (current_response != ref_response)
        
        # Increment the error counter for each cell that flipped
        cell_error_counts += errors

    # --- Analyze and Report Results ---
    print("\n--- Stability Analysis Results ---")
    
    # Calculate the number of stable vs. unstable cells
    stable_cells = np.sum(cell_error_counts == 0)
    unstable_cells = NUM_CELLS - stable_cells
    stability_percentage = (stable_cells / NUM_CELLS) * 100
    
    print(f"Total cells: {NUM_CELLS}")
    print(f"Number of perfectly stable cells (0 errors): {stable_cells}")
    print(f"Number of unstable cells (>0 errors): {unstable_cells}")
    print(f"Percentage of stable cells: {stability_percentage:.2f}%")

    # --- Plotting the Results ---
    output_dir = 'evaluation'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    plt.figure(figsize=(10, 6))
    # Use a log scale on the y-axis to better visualize the rare unstable cells
    plt.hist(cell_error_counts, bins=np.arange(0, NUM_RUNS + 2) - 0.5, rwidth=0.8, log=True)
    plt.title('Distribution of Cell Errors Over 60 Power-Up Cycles')
    plt.xlabel('Number of Times a Cell Flipped (Errors)')
    plt.ylabel('Number of Cells (Log Scale)')
    plt.xticks(np.arange(0, NUM_RUNS + 1, 5))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    output_path = os.path.join(output_dir, 'puf_stability_evaluation.png')
    plt.savefig(output_path)
    print(f"\nHistogram plot saved to '{output_path}'")

if __name__ == "__main__":
    run_stability_evaluation()
