
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.sram_based_puf import SRAM_PUF
from model.ecc.ecc import BCHECC

def test_bch_behavior():
    print("Testing BCH Behavior...")
    num_cells = 1024
    burn_in_rounds = 10
    
    # Create PUF with Burn-in
    puf = SRAM_PUF(num_cells=num_cells, burn_in_rounds=burn_in_rounds, ecc=None)
    stable_len = len(puf.puf_response)
    print(f"PUF created. Stable length: {stable_len}")
    
    if stable_len == 0:
        print("Stable length is 0. Retrying...")
        return

    # Initialize BCH
    try:
        ecc = BCHECC(stable_len, t=5)
    except ValueError as e:
        print(f"BCH Init failed: {e}")
        return

    puf.ecc = ecc
    puf.helper_data = ecc.generate_helper_data(puf.puf_response)
    
    # Generate noisy response
    # Use extreme condition to trigger errors
    temp = 125
    volt = 1.2
    
    # Get raw noisy response (bypass ECC)
    puf.ecc = None
    noisy_response = puf.get_response(temperature=temp, voltage_ratio=volt)
    
    # Calculate Raw BER
    golden = puf.puf_response
    raw_errors = np.sum(noisy_response != golden)
    raw_ber = raw_errors / stable_len
    print(f"Raw Errors: {raw_errors}, Raw BER: {raw_ber:.4f}")
    
    # Apply ECC correction manually
    puf.ecc = ecc
    corrected_response = ecc.correct_data(noisy_response, puf.helper_data)
    
    # Calculate Corrected BER
    ecc_errors = np.sum(corrected_response != golden)
    ecc_ber = ecc_errors / stable_len
    print(f"ECC Errors: {ecc_errors}, ECC BER: {ecc_ber:.4f}")
    
    if ecc_errors > raw_errors:
        print("CRITICAL: ECC increased errors!")
    elif ecc_errors < raw_errors:
        print("ECC reduced errors.")
    else:
        print("ECC had no effect (failure or 0 errors).")

    # Check if ECC fails (returns original)
    if np.array_equal(corrected_response, noisy_response):
        print("ECC returned noisy data (Correction failed or not needed).")
    else:
        print("ECC modified the data.")

if __name__ == "__main__":
    for i in range(5):
        print(f"\n--- Run {i+1} ---")
        test_bch_behavior()
