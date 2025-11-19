import bchlib
import numpy as np

# Test all configurations to see what data length is actually supported
test_configs = [
    {'name': 'BCH(31, 21, t=2)', 'n': 31, 'k': 21, 't': 2},
    {'name': 'BCH(31, 16, t=3)', 'n': 31, 'k': 16, 't': 3},
    {'name': 'BCH(63, 51, t=2)', 'n': 63, 'k': 51, 't': 2},
    {'name': 'BCH(63, 45, t=3)', 'n': 63, 'k': 45, 't': 3},
    {'name': 'BCH(127, 106, t=3)', 'n': 127, 'k': 106, 't': 3},
    {'name': 'BCH(127, 92, t=5)', 'n': 127, 'k': 92, 't': 5},
]

print("BCH Configuration Analysis:")
print("=" * 80)

for config in test_configs:
    name = config['name']
    n, k, t = config['n'], config['k'], config['t']
    m = int(np.log2(n + 1))
    
    bch = bchlib.BCH(t=t, m=m)
    
    max_data_bytes = (bch.n - bch.ecc_bits) // 8
    max_data_bits = max_data_bytes * 8
    
    print(f"\n{name}")
    print(f"  Theoretical: n={n}, k={k} bits, t={t}")
    print(f"  bchlib actual: n={bch.n}, ecc_bits={bch.ecc_bits}")
    print(f"  Max data supported: {max_data_bytes} bytes ({max_data_bits} bits)")
    print(f"  Status: {'✓ OK' if k <= max_data_bits else f'✗ FAIL - need {k} bits but only {max_data_bits} available'}")
