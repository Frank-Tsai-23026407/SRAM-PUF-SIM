# PUF Error Correction Codes (ECC) and Features

This document provides an overview of the features and error correction codes (ECC) implemented in the SRAM-PUF simulator.

## Unstable Cell Identification

The `SRAM_PUF` class supports identifying and masking unstable SRAM cells. Unstable cells are those that do not consistently power up to the same value (0 or 1) due to noise or manufacturing variations. By identifying and excluding these cells, the reliability of the PUF response can be improved.

### How it Works

When the `pre_test_rounds` parameter is set to a value greater than 0 during initialization, the simulator performs a pre-test phase:

1.  The SRAM array is powered up and read multiple times (`pre_test_rounds`).
2.  Cells that flip their value during these rounds (i.e., are not consistently 0 or 1) are marked as unstable.
3.  A mask is created to valid/stable cells.
4.  Subsequent calls to `get_response()` will return data only from the stable cells, effectively filtering out the unstable ones.

### Usage

```python
from model.sram_based_puf import SRAM_PUF

# Initialize with pre-test enabled
# Run 10 power-up cycles to identify unstable cells
puf = SRAM_PUF(rows=64, cols=64, pre_test_rounds=10, pre_test_aging_factor=0.01)

# The response will now only contain bits from stable cells
response = puf.get_response()
print(f"Response length: {len(response)}") # Will be <= 64*64
```

**Note on ECC:** If you use ECC in conjunction with unstable cell identification, be aware that the length of the PUF response will vary depending on the number of stable cells found. Standard ECC implementations often require a fixed data length. Ensure your ECC handling can adapt to variable lengths or that you handle the length mismatch appropriately.

## Implemented ECC Methods

### Hamming Codes

Hamming codes are a family of linear error-correcting codes. They can detect up to two-bit errors or correct one-bit errors.

### BCH Codes

Bose-Chaudhuri-Hocquenghem (BCH) codes are a powerful class of cyclic error-correcting codes. They are a generalization of Hamming codes and can correct multiple random bit errors.

## How to Use ECC

To use a specific ECC method, you need to pass an instance of the corresponding ECC class to the `SRAM_PUF` constructor. Here's an example of how to use each of the implemented methods:

```python
from model.sram_based_puf import SRAM_PUF
from model.ecc.ecc import HammingECC, BCHECC

# Use Hamming code
puf_hamming = SRAM_PUF(rows=64, cols=64, ecc=HammingECC(data_len=64*64))

# Use BCH code
puf_bch = SRAM_PUF(rows=64, cols=64, ecc=BCHECC(data_len=64*64, t=5))
```

| BCH Code | Code Length (n) | Data Length (k) | Error Correction Capability (t) | Redundancy Rate |
|----------|-----------------|-----------------|----------------------------------|-----------------|
| BCH(15, 11, 1) | 15 | 11 | 1 | 73% |
| BCH(15, 7, 2) | 15 | 7 | 2 | 47% |
| BCH(15, 5, 3) | 15 | 5 | 3 | 33% |
| BCH(31, 21, 2) | 31 | 21 | 2 | 68% |
| BCH(31, 16, 3) | 31 | 16 | 3 | 52% |
| BCH(63, 51, 2) | 63 | 51 | 2 | 81% |
| BCH(63, 45, 3) | 63 | 45 | 3 | 71% |
| BCH(127, 106, 3) | 127 | 106 | 3 | 83% |
| BCH(127, 92, 5) | 127 | 92 | 5 | 72% |
