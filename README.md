# SRAM-PUF Simulator

This project provides a Python-based simulation environment for SRAM-based Physical Unclonable Functions (PUFs). It allows for the modeling and analysis of SRAM start-up behavior, and includes features to evaluate PUF quality metrics like uniformity, uniqueness, and reliability under simulated aging conditions. The simulator also implements a Hamming code for error correction to enhance the PUF's stability.

## About PUFs

A Physical Unclonable Function (PUF) is a physical entity that leverages inherent randomness in manufacturing processes to create a unique and unclonable identifier for a physical object, typically an integrated circuit. A PUF is easy to evaluate but hard to predict or duplicate, making it suitable for applications such as secure key generation, authentication, and anti-counterfeiting.

## SRAM-based PUFs

SRAM-based PUFs utilize the random initial state of SRAM cells upon power-up. Each SRAM cell has a preferred state (0 or 1) due to minor manufacturing variations. This pattern of 0s and 1s is unique to each chip and can be used as a digital "fingerprint."

## Features

- **SRAM Cell and Array Simulation:** Models individual SRAM cells and arrays, including the simulation of aging effects.
- **Error Correction:** Implements Hamming code and BCH code for error correction in PUF responses:
    - **Hamming Code:** For single-bit error correction
    - **BCH Code:** For multi-bit error correction with configurable error correction capability
- **PUF Quality Evaluation:** Includes scripts to calculate and plot key PUF quality metrics:
    - **Uniformity:** The balance of 0s and 1s in a PUF response.
    - **Uniqueness:** The difference between responses from multiple PUF instances.
    - **Reliability:** The stability of a PUF's response over time (simulated by an aging factor).
- **BCH Robustness Testing:** Compares different BCH configurations under various aging conditions
- **Testing:** Comes with unit tests to verify the correctness of error correction implementations.

## Getting Started

### Prerequisites

- Python 3.x
- NumPy
- Matplotlib
- bchlib (for BCH error correction)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/SRAM-PUF-SIM.git
    cd SRAM-PUF-SIM
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

### Important Notes on BCH Error Correction

This project uses the `bchlib` library for BCH error correction. Please note:

- **Library Limitations:** The `bchlib` library has specific constraints:
  - Does not support `m=4` (BCH codes with n=15 are not available)
  - Only works with byte-aligned data (data length must be a multiple of 8 bits)
  - Maximum data length is limited by `(n - ecc_bits) // 8` bytes
  
- **Actual BCH Configurations:** Due to these limitations, the actual usable data lengths differ from theoretical BCH code parameters:
  - BCH(31, 16, t=2) - supports 16 bits (not 21 bits theoretically)
  - BCH(31, 16, t=3) - supports 16 bits
  - BCH(63, 48, t=2) - supports 48 bits (not 51 bits)
  - BCH(63, 40, t=3) - supports 40 bits (not 45 bits)
  - BCH(127, 104, t=3) - supports 104 bits (not 106 bits)
  - BCH(127, 88, t=5) - supports 88 bits (not 92 bits)

## Usage

### Running the Evaluation

To evaluate the quality of the simulated PUF and generate a plot of the results, run the `evaluate_puf.py` script:

```bash
python evaluation/evaluate_puf.py
```

This will run a series of simulations with varying aging factors and save a plot named `puf_quality_metrics.png` in the `evaluation` directory.

### Running BCH Robustness Verification

To test and compare different BCH error correction configurations:

```bash
python evaluation/verify_bch_robustness.py
```

This will test multiple BCH configurations (with different error correction capabilities) under various aging factors and generate a comparison plot saved as `bch_robustness_comparison.png`.

### Running the Test

To verify the correctness of the Hamming ECC implementation, run the `test_puf.py` script:

```bash
python test/test_puf.py
```

If the test passes, you will see the message "ECC test passed!".

## Project Structure

```
.
├── model/
│   ├── cell.py              # SRAMCell class
│   ├── sram.py              # SRAM class (array of cells)
│   ├── sram_based_puf.py    # SRAM_PUF class
│   └── ecc/
│       └── ecc.py           # HammingECC and BCHECC classes
├── evaluation/
│   ├── evaluate_puf.py      # Script to evaluate PUF quality
│   ├── verify_bch_robustness.py  # Script to test BCH configurations
│   └── puf_quality_metrics.png   # Example output plot
├── test/
│   └── test_puf.py          # Unit test for the Hamming ECC
├── requirements.txt         # Python dependencies
└── README.md                # This file
```
