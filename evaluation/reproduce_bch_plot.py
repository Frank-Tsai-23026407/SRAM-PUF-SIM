import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.sram_based_puf import SRAM_PUF
from model.ecc.ecc import BCHECC

def run_reproduction():
    print("Reproducing BCH Robustness Plot...")
    
    # Configurations from the image
    configs = [
        {'n': 31,  'k': 16,  't': 2, 'm': 5, 'label': 'BCH(31, 16, t=2)'},
        {'n': 31,  'k': 16,  't': 3, 'm': 5, 'label': 'BCH(31, 16, t=3)'},
        {'n': 63,  'k': 48,  't': 2, 'm': 6, 'label': 'BCH(63, 48, t=2)'},
        {'n': 63,  'k': 40,  't': 3, 'm': 6, 'label': 'BCH(63, 40, t=3)'},
        {'n': 127, 'k': 104, 't': 3, 'm': 7, 'label': 'BCH(127, 104, t=3)'},
        {'n': 127, 'k': 88,  't': 5, 'm': 7, 'label': 'BCH(127, 88, t=5)'},
    ]
    
    aging_factors = np.linspace(0, 0.1, 21) # 0.0 to 0.1 step 0.005
    num_trials = 200
    
    results = {}
    
    for config in configs:
        name = config['label']
        print(f"Testing {name}...")
        
        success_rates = []
        data_len = config['k']
        
        for af in aging_factors:
            successes = 0
            for _ in range(num_trials):
                # Init PUF and ECC
                try:
                    ecc = BCHECC(data_len=data_len, t=config['t'], m=config['m'])
                except ValueError:
                    # Fallback for invalid params if any (shouldn't happen with these values)
                    continue
                    
                puf = SRAM_PUF(num_cells=data_len, ecc=ecc)
                
                golden = puf.puf_response
                
                # Simulate aging/noise
                # Using voltage_ratio as proxy for aging factor based on existing codebase patterns
                # 0.1 aging factor -> 1.1 voltage ratio
                noisy_response = puf.get_response(voltage_ratio=1.0 + af)
                
                if np.array_equal(golden, noisy_response):
                    successes += 1
            
            rate = successes / num_trials
            success_rates.append(rate)
            
        results[name] = success_rates

    # Plotting
    plt.figure(figsize=(12, 8))
    
    markers = ['o', 'o', 'o', 'o', 'o', 'o'] # All circles in the sample? Or varied?
    # The sample image has circles for all, just different colors.
    
    for i, config in enumerate(configs):
        name = config['label']
        rates = results[name]
        plt.plot(aging_factors, rates, marker='o', label=name, markersize=5)
        
    plt.title('BCH ECC Robustness vs. Aging Factor')
    plt.xlabel('Aging Factor (Bit-Flip Probability)')
    plt.ylabel('Success Rate of Correction')
    plt.grid(True, linestyle='--')
    plt.legend()
    plt.ylim(0, 1.05)
    
    output_path = 'evaluation/result/bch_robustness_reproduction.png'
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    run_reproduction()
