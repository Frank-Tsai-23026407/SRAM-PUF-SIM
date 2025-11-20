import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add the project root to the Python path to allow importing from the model package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.sram_based_puf import SRAM_PUF
from model.ecc.ecc import BCHECC, HammingECC

def verify_ecc_robustness(ecc_configs, aging_factors, num_trials=100):
    """
    Verifies the robustness of different ECC configurations under various aging factors.

    :param ecc_configs: A list of dictionaries, each containing an ECC configuration.
    :param aging_factors: An array of aging factors to test.
    :param num_trials: The number of trials for each aging factor.
    :return: A dictionary mapping each configuration name to its list of success rates.
    """
    results = {}

    for config in ecc_configs:
        name = config['name']
        ecc_type = config['type']
        data_len = config['data_len']
        
        print(f"--- Testing {name} ---")
        
        success_rates = []
        
        # The PUF size should match the data length
        puf_size = data_len

        for aging_factor in aging_factors:
            successful_corrections = 0
            for _ in range(num_trials):
                # 1. Initialize PUF and ECC
                # To ensure each trial uses a new PUF, we initialize it inside the loop.
                if ecc_type == 'BCH':
                    ecc = BCHECC(data_len=data_len, t=config['t'], m=config['m'])
                elif ecc_type == 'Hamming':
                    ecc = HammingECC(data_len=data_len)
                else:
                    raise ValueError(f"Unknown ECC type: {ecc_type}")
                
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
    plt.figure(figsize=(14, 8))
    
    # Use different markers and line styles for BCH vs Hamming
    markers = {'BCH': 'o', 'Hamming': 's'}
    linestyles = {'BCH': '-', 'Hamming': '--'}
    
    for name, rates in results.items():
        # Determine if this is BCH or Hamming
        ecc_type = 'BCH' if 'BCH' in name else 'Hamming'
        marker = markers.get(ecc_type, 'o')
        linestyle = linestyles.get(ecc_type, '-')
        
        plt.plot(aging_factors, rates, marker=marker, linestyle=linestyle, 
                label=name, linewidth=2, markersize=6)

    plt.title('ECC Robustness Comparison: BCH vs Hamming', fontsize=14, fontweight='bold')
    plt.xlabel('Aging Factor (Bit-Flip Probability)', fontsize=12)
    plt.ylabel('Success Rate of Correction', fontsize=12)
    plt.grid(True, which='both', linestyle=':', alpha=0.6)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    plt.ylim(0, 1.05)
    plt.tight_layout()
    
    # Save the plot
    output_path = os.path.join(os.path.dirname(__file__), 'ecc_robustness_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to {output_path}")
    plt.show()

def print_efficiency_summary(ecc_configs):
    """Print a summary of code efficiency for each configuration."""
    print("\n" + "="*90)
    print("CODE EFFICIENCY SUMMARY")
    print("="*90)
    print(f"{'Configuration':<25} {'Data Bits':<12} {'Total Bits':<12} {'Redundancy':<14} {'Code Rate':<12} {'Error Cap.'}")
    print("-"*90)
    
    for config in ecc_configs:
        name = config['name']
        data_len = config['data_len']
        ecc_type = config['type']
        
        if ecc_type == 'BCH':
            # Calculate BCH redundancy
            import bchlib
            bch = bchlib.BCH(t=config['t'], m=config['m'])
            redundancy_bits = bch.ecc_bits
            total_bits = bch.n
            error_capability = f"≤ {config['t']} bits"
        elif ecc_type == 'Hamming':
            # Calculate Hamming redundancy
            # For Hamming code: r = ceil(log2(data_len + r + 1))
            r = 0
            while (2**r) < (data_len + r + 1):
                r += 1
            redundancy_bits = r
            total_bits = data_len + r
            error_capability = "1 bit"
        
        code_rate = data_len / total_bits
        
        print(f"{name:<25} {data_len:<12} {total_bits:<12} {redundancy_bits:<14} "
              f"{code_rate:<12.1%} {error_capability}")
    
    print("="*90)

def analyze_efficiency_vs_robustness(results, ecc_configs, aging_factors):
    """Analyze the trade-off between code efficiency and robustness."""
    print("\n" + "="*100)
    print("EFFICIENCY vs ROBUSTNESS ANALYSIS")
    print("="*100)
    
    # Calculate average success rate for each configuration at high aging (last 5 data points)
    print(f"\n{'Configuration':<25} {'Code Rate':<12} {'Avg Success @High Aging':<25} {'Bits Protected/Overhead'}")
    print("-"*100)
    
    for config in ecc_configs:
        name = config['name']
        data_len = config['data_len']
        ecc_type = config['type']
        
        # Calculate code rate and overhead
        if ecc_type == 'BCH':
            import bchlib
            bch = bchlib.BCH(t=config['t'], m=config['m'])
            redundancy_bits = bch.ecc_bits
            total_bits = bch.n
        elif ecc_type == 'Hamming':
            r = 0
            while (2**r) < (data_len + r + 1):
                r += 1
            redundancy_bits = r
            total_bits = data_len + r
        
        code_rate = data_len / total_bits
        bits_per_overhead = data_len / redundancy_bits if redundancy_bits > 0 else float('inf')
        
        # Get average success rate at high aging (last 5 points: aging factor 0.08-0.10)
        success_rates = results[name]
        avg_success_high_aging = np.mean(success_rates[-5:])
        
        print(f"{name:<25} {code_rate:<12.1%} {avg_success_high_aging:<25.1%} {bits_per_overhead:<.2f}")
    
    print("="*100)
    
    # Group comparison: BCH vs Hamming at similar data lengths
    print("\nDIRECT COMPARISON (Same Data Length):")
    print("-"*100)
    
    # Group by similar data lengths
    data_length_groups = {}
    for config in ecc_configs:
        data_len = config['data_len']
        if data_len not in data_length_groups:
            data_length_groups[data_len] = []
        data_length_groups[data_len].append(config)
    
    for data_len in sorted(data_length_groups.keys()):
        configs = data_length_groups[data_len]
        if len(configs) <= 1:
            continue
            
        print(f"\n  Data Length: {data_len} bits")
        print(f"  {'Method':<20} {'Code Rate':<12} {'Redundancy':<12} {'Success @10% Aging':<20} {'Error Cap.'}")
        print(f"  {'-'*85}")
        
        for config in configs:
            name = config['name']
            ecc_type = config['type']
            
            if ecc_type == 'BCH':
                import bchlib
                bch = bchlib.BCH(t=config['t'], m=config['m'])
                redundancy_bits = bch.ecc_bits
                total_bits = bch.n
                error_cap = f"{config['t']} bits"
            else:
                r = 0
                while (2**r) < (data_len + r + 1):
                    r += 1
                redundancy_bits = r
                total_bits = data_len + r
                error_cap = "1 bit"
            
            code_rate = data_len / total_bits
            success_at_10pct = results[name][-1]  # Last point (0.10 aging factor)
            
            method_name = f"{ecc_type}"
            if ecc_type == 'BCH':
                method_name += f" t={config['t']}"
            
            print(f"  {method_name:<20} {code_rate:<12.1%} {redundancy_bits:<12} "
                  f"{success_at_10pct:<20.1%} {error_cap}")
        
        # Calculate efficiency gain
        bch_configs = [c for c in configs if c['type'] == 'BCH']
        hamming_configs = [c for c in configs if c['type'] == 'Hamming']
        
        if bch_configs and hamming_configs:
            for bch_config in bch_configs:
                bch_name = bch_config['name']
                hamming_name = [c['name'] for c in hamming_configs][0]
                
                # Code rate comparison
                import bchlib
                bch = bchlib.BCH(t=bch_config['t'], m=bch_config['m'])
                bch_rate = data_len / bch.n
                
                r = 0
                while (2**r) < (data_len + r + 1):
                    r += 1
                hamming_rate = data_len / (data_len + r)
                
                # Robustness comparison
                bch_success = results[bch_name][-1]
                hamming_success = results[hamming_name][-1]
                
                rate_improvement = ((bch_rate - hamming_rate) / hamming_rate) * 100
                robustness_improvement = ((bch_success - hamming_success) / hamming_success) * 100 if hamming_success > 0 else float('inf')
                
                print(f"\n  → {bch_name} vs {hamming_name}:")
                print(f"     Code rate improvement: {rate_improvement:+.1f}%")
                print(f"     Robustness improvement @10% aging: {robustness_improvement:+.1f}%")
    
    print("\n" + "="*100)

if __name__ == "__main__":
    # Define ECC configurations to be tested (BCH + Hamming for comparison)
    # Note: Due to bchlib's byte-alignment limitation, we use actual supported data lengths
    # We'll compare BCH codes with Hamming codes on similar data lengths
    
    ecc_configurations = [
        # BCH configurations with their parameters
        {'name': 'BCH(31, 16, t=2)', 'type': 'BCH', 'data_len': 16, 't': 2, 'm': 5},
        {'name': 'BCH(31, 16, t=3)', 'type': 'BCH', 'data_len': 16, 't': 3, 'm': 5},
        {'name': 'BCH(63, 48, t=2)', 'type': 'BCH', 'data_len': 48, 't': 2, 'm': 6},
        {'name': 'BCH(63, 40, t=3)', 'type': 'BCH', 'data_len': 40, 't': 3, 'm': 6},
        {'name': 'BCH(127, 104, t=3)', 'type': 'BCH', 'data_len': 104, 't': 3, 'm': 7},
        {'name': 'BCH(127, 88, t=5)', 'type': 'BCH', 'data_len': 88, 't': 5, 'm': 7},
        
        # Hamming configurations with comparable data lengths
        {'name': 'Hamming(16 bits)', 'type': 'Hamming', 'data_len': 16},
        {'name': 'Hamming(48 bits)', 'type': 'Hamming', 'data_len': 48},
        {'name': 'Hamming(40 bits)', 'type': 'Hamming', 'data_len': 40},
        {'name': 'Hamming(104 bits)', 'type': 'Hamming', 'data_len': 104},
        {'name': 'Hamming(88 bits)', 'type': 'Hamming', 'data_len': 88},
    ]

    # Define the range of aging factors to test
    # From 0 (no aging) to 0.1 (10% bit-flip probability)
    aging_factors_to_test = np.linspace(0, 0.1, 21)

    # Print efficiency summary before testing
    print_efficiency_summary(ecc_configurations)
    
    # Run the verification
    print("\n" + "="*80)
    print("STARTING ROBUSTNESS TESTING")
    print("="*80 + "\n")
    robustness_results = verify_ecc_robustness(ecc_configurations, aging_factors_to_test, num_trials=200)

    # Analyze efficiency vs robustness trade-offs
    analyze_efficiency_vs_robustness(robustness_results, ecc_configurations, aging_factors_to_test)

    # Plot the results
    plot_results(robustness_results, aging_factors_to_test)