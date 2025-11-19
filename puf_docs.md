# PUF Error Correction Codes (ECC)

This document provides a brief overview of the error correction codes (ECC) implemented in the SRAM-PUF simulator and explains how to use them.

## Implemented ECC Methods

### Hamming Codes

Hamming codes are a family of linear error-correcting codes. They can detect up to two-bit errors or correct one-bit errors.

### BCH Codes

Bose-Chaudhuri-Hocquenghem (BCH) codes are a powerful class of cyclic error-correcting codes. They are a generalization of Hamming codes and can correct multiple random bit errors.

## How to Use

To use a specific ECC method, you need to pass an instance of the corresponding ECC class to the `SRAM_PUF` constructor. Here's an example of how to use each of the implemented methods:

```python
from model.sram_based_puf import SRAM_PUF
from model.ecc.ecc import HammingECC, BCHECC

# Use Hamming code
puf_hamming = SRAM_PUF(rows=64, cols=64, ecc=HammingECC(data_len=64*64))

# Use BCH code
puf_bch = SRAM_PUF(rows=64, cols=64, ecc=BCHECC(data_len=64*64, t=5))
```
