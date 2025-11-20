# PUF Error Correction Codes (ECC) and Features

This document provides a brief overview of the error correction codes (ECC) implemented in the SRAM-PUF simulator and explains how to use them, as well as other features like Unstable Cell Masking.

## Implemented ECC Methods

### Hamming Codes

Hamming codes are a family of linear error-correcting codes. They can detect up to two-bit errors or correct one-bit errors.

### BCH Codes

Bose-Chaudhuri-Hocquenghem (BCH) codes are a powerful class of cyclic error-correcting codes. They are a generalization of Hamming codes and can correct multiple random bit errors.

## Unstable Cell Masking

The SRAM-PUF simulator includes a feature to identify and mask unstable cells before generating the PUF response. This improves the reliability of the PUF by preventing unstable cells from contributing to the key.

### How it Works

1.  **Pre-Test:** When `pre_test_rounds` is set to a value greater than 0 in the `SRAM_PUF` constructor, the simulator performs a pre-test phase.
2.  **Identification:** The SRAM array is powered up `pre_test_rounds` times at nominal conditions. Cells that flip values during these rounds (i.e., are not consistently 0 or 1) are identified as unstable.
3.  **Masking:** Unstable cells are masked out from the PUF response.
4.  **Result:** The `get_response()` method returns a shorter array containing only the bits from stable cells.

### Usage with ECC

**Important:** When using Unstable Cell Masking, the length of the PUF response will be reduced by the number of unstable cells. If you are also using ECC, the ECC object must be configured to expect the *reduced* data length. Since the number of stable cells is determined at runtime, it is challenging to pre-configure the ECC object with the exact length.

If you need to use ECC with this feature, consider:
1.  Ensuring your ECC implementation handles variable length inputs (if supported).
2.  Or, performing the stability characterization separately first (if possible) to determine the stable count.

## How to Use

To use a specific ECC method, you need to pass an instance of the corresponding ECC class to the `SRAM_PUF` constructor. Here's an example of how to use each of the implemented methods:

```python
from model.sram_based_puf import SRAM_PUF
from model.ecc.ecc import HammingECC, BCHECC

# Use Hamming code
puf_hamming = SRAM_PUF(num_cells=4096, ecc=HammingECC(data_len=4096))

# Use BCH code
puf_bch = SRAM_PUF(num_cells=4096, ecc=BCHECC(data_len=4096, t=5))
```

### Using Unstable Cell Masking

To enable unstable cell masking, set `pre_test_rounds` to a positive integer:

```python
# Enable pre-test with 20 rounds
puf = SRAM_PUF(num_cells=4096, pre_test_rounds=20)

# The response will contain only stable bits
response = puf.get_response()
print(f"Original cells: 4096, Stable cells: {len(response)}")
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
