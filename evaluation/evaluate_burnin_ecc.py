import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from tqdm import tqdm

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.sram_based_puf import SRAM_PUF
from model.ecc.ecc import HammingECC, BCHECC

def evaluate_ber(puf, temp, volt, samples=20):
    """Calculates the Bit Error Rate (BER) for a given PUF configuration."""
    errors = 0
    total_bits = 0

    # Golden response (already masked if applicable)
    golden = puf.puf_response

    if len(golden) == 0:
        # If burn-in masked everything (unlikely but possible), BER is undefined or 0
        return 0.0

    for _ in range(samples):
        try:
            response = puf.get_response(temperature=temp, voltage_ratio=volt)
        except Exception as e:
            print(f"Error generating response: {e}")
            continue

        if len(response) != len(golden):
            print(f"Warning: Length mismatch! {len(response)} vs {len(golden)}")
            continue

        errors += np.sum(response != golden)
        total_bits += len(golden)

    if total_bits == 0:
        return 0.0

    return errors / total_bits

def create_puf_instance(num_cells, use_burn_in, ecc_type, burn_in_rounds=10):
    bi_rounds = burn_in_rounds if use_burn_in else 0

    # Initial PUF creation
    # If using ECC, we typically initialize without ECC first, then attach it,
    # especially if burn-in is used because response length changes.
    puf = SRAM_PUF(num_cells=num_cells, burn_in_rounds=bi_rounds, ecc=None)

    stable_len = len(puf.puf_response)

    if ecc_type == 'Hamming':
        if stable_len > 0:
            ecc = HammingECC(stable_len)
            puf.ecc = ecc
            puf.helper_data = ecc.generate_helper_data(puf.puf_response)

    elif ecc_type == 'BCH':
        if stable_len > 0:
            try:
                # Use t=5 as a reasonable default
                ecc = BCHECC(stable_len, t=5)
                puf.ecc = ecc
                puf.helper_data = ecc.generate_helper_data(puf.puf_response)
            except ValueError as e:
                print(f"Skipping BCH for size {stable_len}: {e}")
                puf.ecc = None

    return puf

def run_experiment():
    num_cells = 1024
    burn_in_rounds = 10
    samples_per_point = 20 # Samples per PUF per condition
    n_pufs = 10 # Number of PUF instances to average over

    temps = [-20, 0, 25, 50, 85, 100, 125]
    volts = [0.8, 0.9, 1.0, 1.1, 1.2]

    # Configurations: Name, use_burn_in, ecc_type
    # ecc_type can be None, 'Hamming', 'BCH'
    config_defs = [
        ("No Burn-in, No ECC", False, None),
        ("Burn-in, No ECC", True, None),
        ("No Burn-in, Hamming", False, 'Hamming'),
        ("Burn-in, Hamming", True, 'Hamming'),
        ("No Burn-in, BCH (t=5)", False, 'BCH'),
        ("Burn-in, BCH (t=5)", True, 'BCH')
    ]

    # Initialize PUF instances
    print(f"Initializing {n_pufs} PUF instances for each of {len(config_defs)} configurations...")
    pufs_collection = {}
    avg_lengths = {}

    print("\n--- Effective PUF Length Summary ---")
    print(f"{'Configuration':<25} | {'Avg Length':<10} | {'Retention':<10}")
    print("-" * 50)

    for name, use_bi, ecc_type in config_defs:
        pufs = []
        lengths = []
        for _ in range(n_pufs):
            p = create_puf_instance(num_cells, use_bi, ecc_type, burn_in_rounds)
            pufs.append(p)
            lengths.append(len(p.puf_response))
        
        pufs_collection[name] = pufs
        avg_len = np.mean(lengths)
        avg_lengths[name] = avg_len
        
        retention = (avg_len / num_cells) * 100
        print(f"{name:<25} | {avg_len:<10.1f} | {retention:<9.1f}%")

    print("-" * 50 + "\n")

    results_temp = {name: [] for name, _, _ in config_defs}
    results_volt = {name: [] for name, _, _ in config_defs}

    # 1. BER vs Temperature (Voltage = 1.0)
    print("Evaluating BER vs Temperature...")
    for temp in tqdm(temps):
        for name, _, _ in config_defs:
            total_ber = 0
            valid_pufs = 0
            for puf in pufs_collection[name]:
                if len(puf.puf_response) == 0: continue
                ber = evaluate_ber(puf, temp, 1.0, samples_per_point)
                total_ber += ber
                valid_pufs += 1

            avg_ber = total_ber / valid_pufs if valid_pufs > 0 else 0
            results_temp[name].append(avg_ber)

    # 2. BER vs Voltage (Temp = 25)
    print("Evaluating BER vs Voltage...")
    for volt in tqdm(volts):
        for name, _, _ in config_defs:
            total_ber = 0
            valid_pufs = 0
            for puf in pufs_collection[name]:
                if len(puf.puf_response) == 0: continue
                ber = evaluate_ber(puf, 25, volt, samples_per_point)
                total_ber += ber
                valid_pufs += 1

            avg_ber = total_ber / valid_pufs if valid_pufs > 0 else 0
            results_volt[name].append(avg_ber)

    # Plotting
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Temp Plot
    for name in results_temp:
        label = f"{name} (L={int(avg_lengths[name])})"
        ax1.plot(temps, results_temp[name], marker='o', label=label)
    ax1.set_title("BER vs Temperature (Voltage=1.0)")
    ax1.set_xlabel("Temperature (C)")
    ax1.set_ylabel("Bit Error Rate")
    ax1.set_yscale('log')
    ax1.grid(True, which="both", ls="-", alpha=0.5)
    ax1.legend()

    # Volt Plot
    for name in results_volt:
        label = f"{name} (L={int(avg_lengths[name])})"
        ax2.plot(volts, results_volt[name], marker='s', label=label)
    ax2.set_title("BER vs Voltage Ratio (Temp=25C)")
    ax2.set_xlabel("Voltage Ratio")
    ax2.set_ylabel("Bit Error Rate")
    ax2.set_yscale('log')
    ax2.grid(True, which="both", ls="-", alpha=0.5)
    ax2.legend()

    plt.tight_layout()
    output_path = 'evaluation/result/burnin_ecc_comparison.png'
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    run_experiment()
