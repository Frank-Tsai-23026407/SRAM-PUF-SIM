import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.sram_based_puf import SRAM_PUF

def hamming_distance(v1, v2):
    """Calculates the Hamming distance between two vectors.

    The Hamming distance is the number of positions at which the corresponding
    symbols are different.

    Args:
        v1 (np.ndarray): The first vector.
        v2 (np.ndarray): The second vector.

    Returns:
        int: The Hamming distance between the two vectors.
    """
    return np.sum(v1 != v2)

def calculate_uniformity(response):
    """Calculates the uniformity of a PUF response.

    Uniformity measures the balance of 0s and 1s in the response. An ideal
    PUF has a uniformity of 50%.

    Args:
        response (np.ndarray): The PUF response to evaluate.

    Returns:
        float: The uniformity of the response, as a percentage.
    """
    return np.mean(response) * 100

def calculate_uniqueness(pufs, num_pufs):
    """Calculates the uniqueness between multiple PUF responses.

    Uniqueness (or inter-chip variation) measures how different the responses
    from different PUF instances are. The ideal value is 50%.

    Args:
        pufs (list of SRAM_PUF): A list of SRAM_PUF objects.
        num_pufs (int): The number of PUFs in the list.

    Returns:
        float: The average uniqueness between all pairs of PUFs, as a percentage.
    """
    total_distance = 0
    num_comparisons = 0
    for i in range(num_pufs):
        for j in range(i + 1, num_pufs):
            total_distance += hamming_distance(pufs[i].puf_response, pufs[j].puf_response)
            num_comparisons += 1
    return (total_distance / (num_comparisons * pufs[0].puf_response.size)) * 100

def calculate_reliability(puf, aging_factor, num_samples=100):
    """Calculates the reliability of a PUF response under aging.

    Reliability (or intra-chip variation) measures how stable a PUF's response
    is under varying conditions. Ideal reliability is 100%.

    Args:
        puf (SRAM_PUF): The SRAM_PUF object to evaluate.
        aging_factor (float): The aging factor to apply.
        num_samples (int, optional): The number of noisy responses to generate.
                                     Defaults to 100.

    Returns:
        float: The reliability of the PUF, as a percentage.
    """
    original_response = puf.puf_response
    total_distance = 0
    for _ in range(num_samples):
        noisy_response = puf.get_response(aging_factor)
        total_distance += hamming_distance(original_response, noisy_response)

    avg_error_rate = total_distance / (num_samples * original_response.size)
    return (1 - avg_error_rate) * 100

def main():
    """Main function to run the PUF evaluation simulation.

    This function initializes simulation parameters, runs the simulations for
    reliability, uniformity, and uniqueness, and plots the results.
    """
    # --- Simulation Parameters ---
    rows, cols = 8, 8
    num_pufs_uniqueness = 50
    aging_factors = np.linspace(0, 0.5, 20)

    # --- Data Storage ---
    uniformity_results = []
    uniqueness_results = []
    reliability_results = []

    # --- Run Simulations ---
    print("Running PUF simulations...")
    for aging in aging_factors:
        # Reliability and Uniformity
        puf_for_reliability = SRAM_PUF(rows, cols)
        reliability = calculate_reliability(puf_for_reliability, aging)
        uniformity = calculate_uniformity(puf_for_reliability.puf_response)
        reliability_results.append(reliability)
        uniformity_results.append(uniformity)

        # Uniqueness (calculated once, as it's independent of aging)
        if not uniqueness_results: # only run once
            pufs_for_uniqueness = [SRAM_PUF(rows, cols) for _ in range(num_pufs_uniqueness)]
            uniqueness = calculate_uniqueness(pufs_for_uniqueness, num_pufs_uniqueness)
            uniqueness_results = [uniqueness] * len(aging_factors)

        print(f"  Aging Factor: {aging:.2f} | Reliability: {reliability:.2f}% | Uniformity: {uniformity:.2f}%")

    print(f"Overall Uniqueness: {uniqueness_results[0]:.2f}%")

    # --- Plotting ---
    plt.figure(figsize=(10, 6))
    plt.plot(aging_factors, reliability_results, marker='o', label='Reliability')
    plt.plot(aging_factors, uniformity_results, marker='s', label='Uniformity')
    plt.plot(aging_factors, uniqueness_results, marker='^', linestyle='--', label='Uniqueness')

    plt.title('PUF Quality Metrics vs. Aging Factor')
    plt.xlabel('Aging Factor (Probability of bit-flip)')
    plt.ylabel('Metric (%)')
    plt.grid(True)
    plt.legend()
    plt.ylim(0, 110)

    # Save the plot
    output_path = 'evaluation/puf_quality_metrics.png'
    plt.savefig(output_path)
    print(f"\\nPlot saved to {output_path}")

if __name__ == "__main__":
    main()
