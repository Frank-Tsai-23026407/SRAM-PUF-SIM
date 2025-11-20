import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

# Add project root to path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.sram_based_puf import SRAM_PUF
from model.ecc.ecc import HammingECC, BCHECC

def calculate_entropy(data):
    """Calculates the Shannon entropy of a binary array."""
    prob = np.sum(data) / len(data)
    if prob == 0 or prob == 1:
        return 0
    return -prob * np.log2(prob) - (1 - prob) * np.log2(1 - prob)

def calculate_ber(golden, noisy):
    """Calculates Bit Error Rate."""
    return np.sum(golden != noisy) / len(golden)

def evaluate_configuration(config):
    """
    Evaluates a single configuration.

    config: dict containing:
        - stability_param
        - voltage_ratio
        - temperature
        - storage_pattern
        - ecc_type ('None', 'Hamming', 'BCH')
        - ecc_kwargs (dict)
        - num_cells
        - aging_cycles (for robustness test)
        - num_samples (for robustness test)
    """

    # Unpack config
    num_cells = config.get('num_cells', 128)
    stability_param = config.get('stability_param', None)

    # Setup ECC
    ecc_type = config.get('ecc_type', 'None')
    ecc_kwargs = config.get('ecc_kwargs', {})

    ecc_instance = None
    if ecc_type == 'Hamming':
        ecc_instance = HammingECC(data_len=num_cells, **ecc_kwargs)
    elif ecc_type == 'BCH':
        ecc_instance = BCHECC(data_len=num_cells, **ecc_kwargs)

    # Initialize PUF
    puf = SRAM_PUF(num_cells=num_cells, ecc=ecc_instance, stability_param=stability_param)

    # 1. Entropy Evaluation
    # We measure entropy of the stored response (raw bits if no ECC, or considering helper data leakage if ECC)

    # Get Golden Response (at nominal conditions)
    golden_response = puf.sram.power_up_array(temperature=25, voltage_ratio=1.0)
    if puf.stable_mask is not None:
        golden_response = golden_response[puf.stable_mask]

    entropy_raw = calculate_entropy(golden_response)

    entropy_reduction = 0
    if ecc_instance:
        # Entropy reduction due to helper data
        if ecc_type == 'BCH':
            helper_data_bits = len(puf.helper_data) * 8 # bytes to bits
        elif ecc_type == 'Hamming':
            helper_data_bits = len(puf.helper_data)
        else:
            helper_data_bits = 0

        entropy_reduction = helper_data_bits / len(golden_response)

    effective_entropy = max(0, entropy_raw - entropy_reduction)

    # 2. Robustness Evaluation (Reliability)
    # We simulate aging and environmental noise

    temp = config.get('temperature', 25)
    volt = config.get('voltage_ratio', 1.0)
    storage_pattern = config.get('storage_pattern', 'static')

    # Apply aging
    # We simulate X cycles of aging with the given storage pattern
    # Note: PUF model accumulates aging internally in cells

    # Pre-aging check (optional, maybe just start with 0)

    # To test robustness, we generate responses under specific temp/volt conditions
    # and compare with golden response (which was corrected if ECC is on)

    # If ECC is on, get_response returns corrected data. We compare with golden raw data (before noise).
    # The 'golden_response' above is raw.
    # If ECC is on, puf.get_response() should return the original data if correction works.

    num_samples = config.get('num_samples', 50)
    total_errors = 0
    total_bits = 0

    # Simulate some aging first? The prompt implies "robustness of each configuration... storage_pattern"
    # storage_pattern affects aging. So we should age the device.
    # Let's age it for a fixed number of cycles (e.g. 1000) using the specified storage_pattern.
    aging_cycles = config.get('aging_cycles', 100) # Default 100 for speed

    # We manually age the cells because get_response updates age but we want to control the pattern
    # Actually puf.get_response(..., storage_pattern=...) updates the age.
    # So we can just loop calling get_response to age it.

    for _ in range(aging_cycles):
        puf.get_response(temperature=25, voltage_ratio=1.0, storage_pattern=storage_pattern)

    # Now measure reliability at the specific environmental condition
    for _ in range(num_samples):
        # get_response returns corrected data if ECC is enabled
        # or raw data if ECC is disabled.
        response = puf.get_response(temperature=temp, voltage_ratio=volt, storage_pattern=storage_pattern)

        # Compare with golden_response
        # Note: golden_response is the one generated at init (nominal conditions).
        # Ideally, ECC should recover THIS specific golden response.

        total_errors += np.sum(response != golden_response)
        total_bits += len(golden_response)

    ber = total_errors / total_bits
    reliability = 1.0 - ber

    return {
        'entropy_raw': entropy_raw,
        'entropy_reduction': entropy_reduction,
        'effective_entropy': effective_entropy,
        'reliability': reliability,
        'ber': ber
    }

def main():
    results = []

    # Define parameter ranges
    stability_params = [None, 0.6, 0.7, 0.8, 0.9] # None means random distribution
    voltage_ratios = [0.8, 1.0, 1.2]
    temperatures = [0, 25, 85]
    storage_patterns = ['static', 'random', 'optimized']

    ecc_configs = [
        {'type': 'None', 'kwargs': {}},
        {'type': 'Hamming', 'kwargs': {}},
        {'type': 'BCH', 'kwargs': {'t': 2}},
        {'type': 'BCH', 'kwargs': {'t': 5}}
    ]

    # Reduced set for demonstration/speed if needed, but let's try to be comprehensive
    # Total combinations: 5 * 3 * 3 * 3 * 4 = 540. Might be slow.
    # Let's prioritize key variations.

    # Base configuration defaults
    default_stability = None
    default_voltage = 1.0
    default_temp = 25
    default_pattern = 'static'
    default_ecc = {'type': 'None', 'kwargs': {}}

    # 1. Vary Stability
    print("Evaluating Stability variations...")
    for stab in stability_params:
        for ecc in ecc_configs:
            config = {
                'stability_param': stab,
                'voltage_ratio': default_voltage,
                'temperature': default_temp,
                'storage_pattern': default_pattern,
                'ecc_type': ecc['type'],
                'ecc_kwargs': ecc['kwargs'],
                'aging_cycles': 200
            }
            res = evaluate_configuration(config)
            res.update(config)
            res['ecc_str'] = f"{ecc['type']}" + (f"(t={ecc['kwargs'].get('t')})" if 't' in ecc['kwargs'] else "")
            res['variation_type'] = 'stability'
            results.append(res)

    # 2. Vary Environment (Voltage, Temp) & Storage Pattern (Aging)
    # We fix stability to default (random distribution) and vary others
    print("Evaluating Environment & Storage variations...")

    # Iterate over Environmental Conditions
    for volt in voltage_ratios:
        for temp in temperatures:
            for pattern in storage_patterns:
                for ecc in ecc_configs:
                    # Skip default case if already covered (strictly speaking we haven't covered all combinations above)
                    # but let's just run it.

                    config = {
                        'stability_param': default_stability,
                        'voltage_ratio': volt,
                        'temperature': temp,
                        'storage_pattern': pattern,
                        'ecc_type': ecc['type'],
                        'ecc_kwargs': ecc['kwargs'],
                        'aging_cycles': 200
                    }
                    res = evaluate_configuration(config)
                    res.update(config)
                    res['ecc_str'] = f"{ecc['type']}" + (f"(t={ecc['kwargs'].get('t')})" if 't' in ecc['kwargs'] else "")
                    res['variation_type'] = 'environment'
                    results.append(res)

    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(results)

    # Print Summary Tables
    print("\n--- Summary: Effect of Stability Parameter (averaged over ECCs) ---")
    print(df[df['variation_type'] == 'stability'].groupby(['stability_param', 'ecc_str'])[['reliability', 'effective_entropy']].mean())

    print("\n--- Summary: Effect of Storage Pattern (averaged) ---")
    print(df[df['variation_type'] == 'environment'].groupby(['storage_pattern', 'ecc_str'])[['reliability']].mean())

    print("\n--- Summary: Effect of Voltage/Temp (averaged) ---")
    print(df[df['variation_type'] == 'environment'].groupby(['voltage_ratio', 'temperature', 'ecc_str'])[['reliability']].mean())

    # Save detailed results
    df.to_csv('evaluation/comprehensive_evaluation_results.csv')
    print("\nDetailed results saved to evaluation/comprehensive_evaluation_results.csv")

    # --- Plotting ---
    # 1. Robustness vs Stability
    plt.figure(figsize=(10, 6))
    df_stab = df[df['variation_type'] == 'stability'].copy()
    # Replace None stability with 'Random' for plotting
    df_stab['stability_param'] = df_stab['stability_param'].fillna('Random')

    # Since 'Random' is mixed types with floats, we should handle x-axis labels carefully
    unique_stabs = df_stab['stability_param'].unique()
    # Sort: Random first, then numbers
    sorted_stabs = sorted([x for x in unique_stabs if x != 'Random'])
    if 'Random' in unique_stabs:
        sorted_stabs = ['Random'] + sorted_stabs

    for ecc in df_stab['ecc_str'].unique():
        subset = df_stab[df_stab['ecc_str'] == ecc]
        # Group by stability param to get mean reliability
        means = subset.groupby('stability_param')['reliability'].mean().reindex(sorted_stabs)
        plt.plot(range(len(sorted_stabs)), means, marker='o', label=ecc)

    plt.xticks(range(len(sorted_stabs)), sorted_stabs)
    plt.title('Robustness (Reliability) vs Cell Stability Parameter')
    plt.xlabel('Stability Parameter (Higher is more stable)')
    plt.ylabel('Reliability (1 - BER)')
    plt.ylim(0.5, 1.05)
    plt.grid(True)
    plt.legend()
    plt.savefig('evaluation/robustness_vs_stability.png')
    print("Plot saved: evaluation/robustness_vs_stability.png")

    # 2. Entropy vs ECC
    plt.figure(figsize=(8, 6))
    # Use stability variation data but group by ECC
    entropy_means = df_stab.groupby('ecc_str')['effective_entropy'].mean()
    entropy_means.plot(kind='bar')
    plt.title('Effective Entropy vs ECC Configuration')
    plt.ylabel('Effective Entropy (bits/cell)')
    plt.tight_layout()
    plt.savefig('evaluation/entropy_vs_ecc.png')
    print("Plot saved: evaluation/entropy_vs_ecc.png")

    # 3. Robustness vs Aging (Storage Pattern)
    # We averaged over voltage/temp in the loop, let's look at storage patterns effect
    plt.figure(figsize=(10, 6))
    df_env = df[df['variation_type'] == 'environment']
    # We want to see how different storage patterns affect reliability (averaged over temp/volt)

    for ecc in df_env['ecc_str'].unique():
        subset = df_env[df_env['ecc_str'] == ecc]
        means = subset.groupby('storage_pattern')['reliability'].mean()
        plt.plot(means.index, means.values, marker='o', label=ecc)

    plt.title('Robustness vs Storage Pattern (Aging Effect)')
    plt.xlabel('Storage Pattern')
    plt.ylabel('Reliability')
    plt.grid(True)
    plt.legend()
    plt.savefig('evaluation/robustness_vs_storage.png')
    print("Plot saved: evaluation/robustness_vs_storage.png")

    # 4. Robustness vs Temperature (averaged over others)
    plt.figure(figsize=(10, 6))
    for ecc in df_env['ecc_str'].unique():
        subset = df_env[df_env['ecc_str'] == ecc]
        means = subset.groupby('temperature')['reliability'].mean()
        plt.plot(means.index, means.values, marker='o', label=ecc)

    plt.title('Robustness vs Temperature')
    plt.xlabel('Temperature (C)')
    plt.ylabel('Reliability')
    plt.grid(True)
    plt.legend()
    plt.savefig('evaluation/robustness_vs_temp.png')
    print("Plot saved: evaluation/robustness_vs_temp.png")


if __name__ == "__main__":
    main()
