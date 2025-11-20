"""
Test script to verify the effectiveness of burn-in-test functionality.
This script compares PUF performance with and without burn-in-test.
"""

import sys
import os
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.sram_based_puf import SRAM_PUF
from model.ecc.ecc import HammingECC


def calculate_bit_error_rate(original, noisy):
    """Calculate the Bit Error Rate (BER) between two responses."""
    if len(original) != len(noisy):
        raise ValueError(f"Length mismatch: {len(original)} vs {len(noisy)}")
    return np.sum(original != noisy) / len(original)


def test_without_pretest(num_cells=1024, test_rounds=50):
    """Test PUF without burn-in-test."""
    print("=" * 60)
    print("Testing WITHOUT burn-in-test")
    print("=" * 60)
    
    # Create PUF without burn-in-test
    puf = SRAM_PUF(num_cells=num_cells, ecc=None, burn_in_rounds=0)
    
    print(f"Total cells: {num_cells}")
    print(f"Stable mask: {puf.stable_mask}")
    print(f"Response length: {len(puf.puf_response)}")
    
    # Test reliability under various conditions
    errors = []
    
    for i in range(test_rounds):
        # Test under nominal conditions
        response = puf.get_response(temperature=25, voltage_ratio=1.0)
        ber = calculate_bit_error_rate(puf.puf_response, response)
        errors.append(ber)
    
    avg_ber = np.mean(errors)
    max_ber = np.max(errors)
    min_ber = np.min(errors)
    std_ber = np.std(errors)
    
    print(f"\nReliability Test (Nominal Conditions, {test_rounds} rounds):")
    print(f"  Average BER: {avg_ber:.6f} ({avg_ber*100:.4f}%)")
    print(f"  Min BER: {min_ber:.6f}")
    print(f"  Max BER: {max_ber:.6f}")
    print(f"  Std BER: {std_ber:.6f}")
    
    # Test under varying temperature
    temp_errors = []
    temperatures = [20, 25, 30, 35, 40]
    
    print(f"\nTemperature Variation Test:")
    for temp in temperatures:
        response = puf.get_response(temperature=temp, voltage_ratio=1.0)
        ber = calculate_bit_error_rate(puf.puf_response, response)
        temp_errors.append(ber)
        print(f"  Temp {temp}°C: BER = {ber:.6f} ({ber*100:.4f}%)")
    
    return {
        'avg_ber_nominal': avg_ber,
        'max_ber_nominal': max_ber,
        'std_ber_nominal': std_ber,
        'temp_errors': temp_errors,
        'response_length': len(puf.puf_response),
        'stable_count': num_cells  # All cells are used
    }


def test_with_pretest(num_cells=1024, burn_in_test_rounds=10, test_rounds=50):
    """Test PUF with burn-in-test."""
    print("\n" + "=" * 60)
    print(f"Testing WITH burn-in-test ({burn_in_test_rounds} rounds)")
    print("=" * 60)
    
    # Create PUF with burn-in-test
    puf = SRAM_PUF(num_cells=num_cells, ecc=None, burn_in_rounds=burn_in_test_rounds)
    
    stable_count = np.sum(puf.stable_mask) if puf.stable_mask is not None else num_cells
    unstable_count = num_cells - stable_count
    
    print(f"Total cells: {num_cells}")
    print(f"Stable cells identified: {stable_count} ({stable_count/num_cells*100:.2f}%)")
    print(f"Unstable cells filtered: {unstable_count} ({unstable_count/num_cells*100:.2f}%)")
    print(f"Response length: {len(puf.puf_response)}")
    
    # Test reliability under various conditions
    errors = []
    
    for i in range(test_rounds):
        # Test under nominal conditions
        response = puf.get_response(temperature=25, voltage_ratio=1.0)
        ber = calculate_bit_error_rate(puf.puf_response, response)
        errors.append(ber)
    
    avg_ber = np.mean(errors)
    max_ber = np.max(errors)
    min_ber = np.min(errors)
    std_ber = np.std(errors)
    
    print(f"\nReliability Test (Nominal Conditions, {test_rounds} rounds):")
    print(f"  Average BER: {avg_ber:.6f} ({avg_ber*100:.4f}%)")
    print(f"  Min BER: {min_ber:.6f}")
    print(f"  Max BER: {max_ber:.6f}")
    print(f"  Std BER: {std_ber:.6f}")
    
    # Test under varying temperature
    temp_errors = []
    temperatures = [20, 25, 30, 35, 40]
    
    print(f"\nTemperature Variation Test:")
    for temp in temperatures:
        response = puf.get_response(temperature=temp, voltage_ratio=1.0)
        ber = calculate_bit_error_rate(puf.puf_response, response)
        temp_errors.append(ber)
        print(f"  Temp {temp}°C: BER = {ber:.6f} ({ber*100:.4f}%)")
    
    return {
        'avg_ber_nominal': avg_ber,
        'max_ber_nominal': max_ber,
        'std_ber_nominal': std_ber,
        'temp_errors': temp_errors,
        'response_length': len(puf.puf_response),
        'stable_count': stable_count
    }


def compare_results(without_pretest, with_pretest):
    """Compare and print the results."""
    print("\n" + "=" * 60)
    print("COMPARISON: With vs Without burn-in-test")
    print("=" * 60)
    
    print(f"\nResponse Length:")
    print(f"  Without burn-in-test: {without_pretest['response_length']} bits")
    print(f"  With burn-in-test: {with_pretest['response_length']} bits")
    print(f"  Reduction: {without_pretest['response_length'] - with_pretest['response_length']} bits "
          f"({(1 - with_pretest['response_length']/without_pretest['response_length'])*100:.2f}%)")
    
    print(f"\nAverage BER (Nominal Conditions):")
    print(f"  Without burn-in-test: {without_pretest['avg_ber_nominal']:.6f} ({without_pretest['avg_ber_nominal']*100:.4f}%)")
    print(f"  With burn-in-test: {with_pretest['avg_ber_nominal']:.6f} ({with_pretest['avg_ber_nominal']*100:.4f}%)")
    
    if without_pretest['avg_ber_nominal'] > 0:
        improvement = (without_pretest['avg_ber_nominal'] - with_pretest['avg_ber_nominal']) / without_pretest['avg_ber_nominal'] * 100
        print(f"  Improvement: {improvement:.2f}%")
    
    print(f"\nMax BER (Nominal Conditions):")
    print(f"  Without burn-in-test: {without_pretest['max_ber_nominal']:.6f}")
    print(f"  With burn-in-test: {with_pretest['max_ber_nominal']:.6f}")
    
    print(f"\nStd BER (Nominal Conditions):")
    print(f"  Without burn-in-test: {without_pretest['std_ber_nominal']:.6f}")
    print(f"  With burn-in-test: {with_pretest['std_ber_nominal']:.6f}")
    
    print(f"\nTemperature Robustness (Average BER across temps):")
    avg_temp_without = np.mean(without_pretest['temp_errors'])
    avg_temp_with = np.mean(with_pretest['temp_errors'])
    print(f"  Without burn-in-test: {avg_temp_without:.6f} ({avg_temp_without*100:.4f}%)")
    print(f"  With burn-in-test: {avg_temp_with:.6f} ({avg_temp_with*100:.4f}%)")
    
    if avg_temp_without > 0:
        temp_improvement = (avg_temp_without - avg_temp_with) / avg_temp_without * 100
        print(f"  Improvement: {temp_improvement:.2f}%")
    
    print("\n" + "=" * 60)
    print("CONCLUSION:")
    print("=" * 60)
    
    if with_pretest['avg_ber_nominal'] < without_pretest['avg_ber_nominal']:
        print("✓ burn-in-test is EFFECTIVE: BER decreased")
        print(f"  The burn-in-test reduced errors by filtering out unstable cells.")
    elif with_pretest['avg_ber_nominal'] == without_pretest['avg_ber_nominal']:
        print("≈ burn-in-test has NEUTRAL effect: BER unchanged")
        print(f"  The burn-in-test didn't improve reliability, possibly because cells are naturally stable.")
    else:
        print("✗ burn-in-test is INEFFECTIVE: BER increased")
        print(f"  This is unexpected and may indicate an implementation issue.")
    
    print(f"\nTrade-off: You lose {without_pretest['response_length'] - with_pretest['response_length']} bits "
          f"but gain improved reliability.")


def main():
    """Main test function."""
    print("=" * 60)
    print("PUF burn-in-test EFFECTIVENESS EVALUATION")
    print("=" * 60)
    print()
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Test parameters
    num_cells = 1024
    burn_in_test_rounds = 10
    test_rounds = 50
    
    print(f"Test Configuration:")
    print(f"  Number of cells: {num_cells}")
    print(f"  burn-in-test rounds: {burn_in_test_rounds}")
    print(f"  Reliability test rounds: {test_rounds}")
    print()
    
    # Run tests
    results_without = test_without_pretest(num_cells=num_cells, test_rounds=test_rounds)
    results_with = test_with_pretest(num_cells=num_cells, burn_in_test_rounds=burn_in_test_rounds, test_rounds=test_rounds)
    
    # Compare results
    compare_results(results_without, results_with)


if __name__ == '__main__':
    main()
