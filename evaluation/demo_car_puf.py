import sys
import os
import numpy as np

# Add project root to path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.car_puf import CarPUF

def main():
    print("=== Automotive SRAM PUF Demo ===\n")

    # 1. Initialization (Enrollment Phase)
    print("1. Initializing CarPUF (Enrollment with Burn-in)...")
    # We use a small array for demo speed, but enough for BCH
    # BCH(n, t=5) needs some space. 255 bits is common for BCH.
    # Let's use 511 cells to be safe.
    car_puf = CarPUF(num_cells=511, ecc_t=15, burn_in_rounds=10)

    print(f"   Golden Key generated. Length: {len(car_puf.golden_response)}")
    print(f"   Masked Cells: {511 - len(car_puf.golden_response)} (unstable cells removed)")
    print("   Enrollment Complete.\n")

    # 2. Testing across Temperature Range (ISO 26262 / AEC-Q100)
    print("2. Testing Reliability across Temperatures...")
    temperatures = [-40, 0, 25, 85, 125, 150]

    all_passed = True
    for temp in temperatures:
        print(f"   Testing at {temp}°C...", end=" ")

        # Get corrected key
        key = car_puf.get_response(temperature=temp)

        # Verify
        if np.array_equal(key, car_puf.golden_response):
            print("SUCCESS (Key recovered)")
        else:
            print("FAILURE (Key mismatch)")
            all_passed = False

    if all_passed:
        print("   -> Passed all temperature checks.\n")
    else:
        print("   -> FAILED temperature checks.\n")

    # 3. Simulate Aging (15 Years)
    print("3. Simulating 15-Year Lifespan (Aging)...")

    # 15 years * 365 days * 24 hours = ~131,400 hours
    lifespan_hours = 131400

    # Simulate in chunks to show degradation monitoring
    for year in [1, 5, 10, 15]:
        hours_to_add = (year * 8760) - car_puf.current_age_hours
        car_puf.simulate_aging(hours=hours_to_add, temperature_profile=85)

        health = car_puf.check_health()
        print(f"   Year {year}: BER = {health['ber']:.4f} ({health['errors']} bit errors). Status: {health['status']}")

        # Try to recover key at high temp (worst case)
        key_at_high_temp = car_puf.get_response(temperature=125)
        if np.array_equal(key_at_high_temp, car_puf.golden_response):
             print(f"      Key Recovery at 125°C: OK")
        else:
             print(f"      Key Recovery at 125°C: FAILED")

    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    main()
