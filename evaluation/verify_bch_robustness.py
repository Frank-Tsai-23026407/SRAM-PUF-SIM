import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add the project root to the Python path to allow importing from the model package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.sram_based_puf import SRAM_PUF
from model.ecc.ecc import BCHECC

def verify_bch_robustness(bch_configs, aging_factors, num_trials=100):
    """
    Verifies the robustness of different BCH configurations under various aging factors.

    :param bch_configs: A list of dictionaries, each containing a BCH configuration.
    :param aging_factors: An array of aging factors to test.
    :param num_trials: The number of trials for each aging factor.
    :return: A dictionary mapping each configuration name to its list of success rates.
    """
    results = {}

    for config in bch_configs:
        name = config['name']
        n, k, t = config['n'], config['k'], config['t']
        print(f"--- Testing {name} ---")
        
        # Calculate m from n (since n = 2^m - 1)
        m = int(np.log2(n + 1))
        
        success_rates = []
        
        # The PUF size should match the data length k (not the codeword length n)
        # because BCH encoding will add redundancy bits to create the full codeword
        puf_size = k

        for aging_factor in aging_factors:
            successful_corrections = 0
            for _ in range(num_trials):
                # 1. Initialize PUF and ECC
                # To ensure each trial uses a new PUF, we initialize it inside the loop.
                ecc = BCHECC(data_len=k, t=t, m=m)
                puf = SRAM_PUF(rows=1, cols=puf_size, ecc=ecc)

                # 2. Get the original PUF response (without aging)
                original_response = puf.puf_response

                # 3. Get the response with aging effects, corrected by ECC.
                # get_response internally simulates aging and performs correction.
                corrected_response = puf.get_response(aging_factor=aging_factor)

                # 4. Compare if the corrected response matches the original response.
                if np.array_equal(original_response, corrected_response):
                    successful_corrections += 1
            
            success_rate = successful_corrections / num_trials
            success_rates.append(success_rate)
            print(f"  Aging Factor: {aging_factor:.3f}, Success Rate: {success_rate:.2%}")

        results[name] = success_rates
        
    return results

def plot_results(results, aging_factors):
    """Plots the results into a chart."""
    plt.figure(figsize=(12, 8))
    for name, rates in results.items():
        plt.plot(aging_factors, rates, marker='o', linestyle='-', label=name)

    plt.title('BCH ECC Robustness vs. Aging Factor')
    plt.xlabel('Aging Factor (Bit-Flip Probability)')
    plt.ylabel('Success Rate of Correction')
    plt.grid(True, which='both', linestyle='--')
    plt.legend()
    plt.ylim(0, 1.05)
    
    # Save the plot
    output_path = os.path.join(os.path.dirname(__file__), 'bch_robustness_comparison.png')
    plt.savefig(output_path)
    print(f"\nPlot saved to {output_path}")
    plt.show()

if __name__ == "__main__":
    # Define the BCH configurations to be tested
    # Define the BCH configurations to be tested
    # Note: Due to bchlib's byte-alignment limitation, we use actual supported data lengths
    # Format: k_actual = ((n - ecc_bits) // 8) * 8
    bch_configurations = [
        # BCH(31, k, t=2): n=31, ecc_bits=10, max_data=2 bytes=16 bits
        {'name': 'BCH(31, 16, t=2)', 'n': 31, 'k': 16, 't': 2},
        # BCH(31, k, t=3): n=31, ecc_bits=15, max_data=2 bytes=16 bits  
        {'name': 'BCH(31, 16, t=3)', 'n': 31, 'k': 16, 't': 3},
        # BCH(63, k, t=2): n=63, ecc_bits=12, max_data=6 bytes=48 bits
        {'name': 'BCH(63, 48, t=2)', 'n': 63, 'k': 48, 't': 2},
        # BCH(63, k, t=3): n=63, ecc_bits=18, max_data=5 bytes=40 bits
        {'name': 'BCH(63, 40, t=3)', 'n': 63, 'k': 40, 't': 3},
        # BCH(127, k, t=3): n=127, ecc_bits=21, max_data=13 bytes=104 bits
        {'name': 'BCH(127, 104, t=3)', 'n': 127, 'k': 104, 't': 3},
        # BCH(127, k, t=5): n=127, ecc_bits=35, max_data=11 bytes=88 bits
        {'name': 'BCH(127, 88, t=5)', 'n': 127, 'k': 88, 't': 5},
    ]

    # Define the range of aging factors to test
    # From 0 (no aging) to 0.1 (10% bit-flip probability)
    aging_factors_to_test = np.linspace(0, 0.1, 21)

    # Run the verification
    robustness_results = verify_bch_robustness(bch_configurations, aging_factors_to_test, num_trials=200)

    # Plot the results
    plot_results(robustness_results, aging_factors_to_test)