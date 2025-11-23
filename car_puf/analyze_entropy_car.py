import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from car_puf.car_puf import CarPUF
from model.ecc.ecc import BCHECC

def calculate_shannon_entropy(data):
    """Calculates Shannon entropy of a bit string/array."""
    if len(data) == 0:
        return 0.0
    p1 = np.mean(data)
    p0 = 1.0 - p1
    if p0 == 0 or p1 == 0:
        return 0.0
    return -p0 * np.log2(p0) - p1 * np.log2(p1)

def run_entropy_test(num_cells, burn_in_rounds, ecc_t):
    """Runs a single test case and returns entropy metrics."""
    try:
        # Initialize CarPUF
        # Note: CarPUF determines stable bits during init
        puf = CarPUF(num_cells=num_cells, ecc_t=ecc_t, burn_in_rounds=burn_in_rounds)

        # 1. Raw Capacity (Total cells)
        total_cells = num_cells

        # 2. Masking Loss
        # stable_mask is in puf.puf_core.stable_mask
        if puf.puf_core.stable_mask is not None:
            stable_count = np.sum(puf.puf_core.stable_mask)
        else:
            stable_count = num_cells

        masked_bits_loss = total_cells - stable_count

        # 3. Raw Entropy of Stable Bits
        # Ideally close to 1.0 per bit if unbiased
        raw_entropy_per_bit = calculate_shannon_entropy(puf.golden_response)
        total_raw_entropy = raw_entropy_per_bit * stable_count

        # 4. ECC Leakage (Helper Data)
        # For BCH, helper data is the parity bits.
        # BCHECC stores helper data as bytes.
        helper_data_bytes = len(puf.puf_core.helper_data)
        helper_data_bits = helper_data_bytes * 8

        # IMPORTANT: BCH helper data size depends on 'm' and 't'.
        # The bchlib helper data usually includes padding to byte boundaries.
        # We should consider the theoretical leakage: m * t.
        # But let's use the actual stored size for a conservative estimate.

        # 5. Effective Entropy (Remaining Secret)
        # Entropy = Stable_Bits_Entropy - Helper_Data_Leakage
        effective_entropy_bits = total_raw_entropy - helper_data_bits

        return {
            "num_cells": num_cells,
            "burn_in": burn_in_rounds,
            "ecc_t": ecc_t,
            "stable_count": int(stable_count),
            "mask_loss": int(masked_bits_loss),
            "raw_entropy_per_bit": raw_entropy_per_bit,
            "helper_data_bits": helper_data_bits,
            "effective_entropy": effective_entropy_bits,
            "effective_entropy_per_cell": effective_entropy_bits / num_cells
        }

    except RuntimeError as e:
        # Case where initialization fails (too few stable bits)
        return {
            "num_cells": num_cells,
            "burn_in": burn_in_rounds,
            "ecc_t": ecc_t,
            "error": str(e)
        }

def main():
    print("=== Automotive PUF Entropy Analysis ===\n")

    # Define test matrix
    # We keep num_cells constant to compare efficiency
    NUM_CELLS = 1024

    # Configurations to test
    burn_in_options = [0, 5, 10, 20]
    ecc_t_options = [5, 10, 15, 20]

    results = []

    print(f"{'Burn-In':<10} | {'ECC T':<5} | {'Stable':<8} | {'Mask Loss':<10} | {'Helper(b)':<10} | {'Eff. Ent.':<10} | {'Ent/Cell':<8}")
    print("-" * 85)

    for b_rounds in burn_in_options:
        for t in ecc_t_options:
            # We average over a few runs to smooth out random stability init
            metrics_sum = None
            runs = 5
            valid_runs = 0

            for _ in range(runs):
                res = run_entropy_test(NUM_CELLS, b_rounds, t)
                if "error" in res:
                    continue

                if metrics_sum is None:
                    metrics_sum = res
                    metrics_sum['raw_entropy_per_bit'] = 0 # Accumulate separately
                else:
                    metrics_sum['stable_count'] += res['stable_count']
                    metrics_sum['mask_loss'] += res['mask_loss']
                    metrics_sum['helper_data_bits'] += res['helper_data_bits']
                    metrics_sum['effective_entropy'] += res['effective_entropy']

                metrics_sum['raw_entropy_per_bit'] += res['raw_entropy_per_bit']
                valid_runs += 1

            if valid_runs > 0:
                # Average results
                avg_res = metrics_sum
                avg_res['stable_count'] /= valid_runs
                avg_res['mask_loss'] /= valid_runs
                avg_res['helper_data_bits'] /= valid_runs
                avg_res['effective_entropy'] /= valid_runs
                avg_res['raw_entropy_per_bit'] /= valid_runs
                avg_res['effective_entropy_per_cell'] = avg_res['effective_entropy'] / NUM_CELLS

                results.append(avg_res)

                print(f"{b_rounds:<10} | {t:<5} | {avg_res['stable_count']:<8.1f} | {avg_res['mask_loss']:<10.1f} | {avg_res['helper_data_bits']:<10.1f} | {avg_res['effective_entropy']:<10.1f} | {avg_res['effective_entropy_per_cell']:<8.3f}")
            else:
                print(f"{b_rounds:<10} | {t:<5} | FAILED TO INIT (Too few stable cells)")

    print("\nAnalysis Complete.")

if __name__ == "__main__":
    main()
