# SRAM-PUF Simulator

This project provides a Python-based simulation environment for SRAM-based Physical Unclonable Functions (PUFs). It allows for the modeling and analysis of SRAM start-up behavior, and includes features to evaluate PUF quality metrics like uniformity, uniqueness, and reliability under simulated aging conditions. The simulator also implements a Hamming code for error correction to enhance the PUF's stability.

## About PUFs

A Physical Unclonable Function (PUF) is a physical entity that leverages inherent randomness in manufacturing processes to create a unique and unclonable identifier for a physical object, typically an integrated circuit. A PUF is easy to evaluate but hard to predict or duplicate, making it suitable for applications such as secure key generation, authentication, and anti-counterfeiting.

## SRAM-based PUFs

SRAM-based PUFs utilize the random initial state of SRAM cells upon power-up. Each SRAM cell has a preferred state (0 or 1) due to minor manufacturing variations. This pattern of 0s and 1s is unique to each chip and can be used as a digital "fingerprint."

## Features

- **SRAM Cell and Array Simulation:** Models individual SRAM cells and arrays, including the simulation of aging effects (NBTI, HCI).
- **Error Correction:** Implements Hamming code and BCH code for error correction in PUF responses:
    - **Hamming Code:** For single-bit error correction.
    - **BCH Code:** For multi-bit error correction with configurable error correction capability using `bchlib`.
- **PUF Quality Evaluation:** Includes scripts to calculate and plot key PUF quality metrics:
    - **Uniformity:** The balance of 0s and 1s in a PUF response.
    - **Uniqueness:** The difference between responses from multiple PUF instances.
    - **Reliability:** The stability of a PUF's response over time (simulated by an aging factor).
- **BCH Robustness Testing:** Compares different BCH configurations under various aging conditions.
- **Entropy Analysis:** Tools to analyze the entropy of the PUF response and the impact of ECC helper data.
- **Comprehensive Evaluation:** A script to sweep across varying stability parameters, environmental conditions, and ECC configurations.

## Getting Started

### Prerequisites

- Python 3.x
- NumPy
- Matplotlib
- bchlib (for BCH error correction)
- pandas (for data analysis)
- tqdm (for progress bars)

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
  - Does not support `m=4` (BCH codes with n=15 are not available).
  - Only works with byte-aligned data (data length must be a multiple of 8 bits).
  - Maximum data length is limited by `(n - ecc_bits) // 8` bytes.

- **Actual BCH Configurations:** Due to these limitations, the actual usable data lengths differ from theoretical BCH code parameters. See `evaluation/verify_bch_robustness.py` for details.

## Usage

### Running the Evaluation

To evaluate the quality of the simulated PUF and generate a plot of the results, run the `evaluate_puf.py` script:

```bash
python evaluation/evaluate_puf.py
```

This will run a series of simulations with varying aging factors and save a plot named `puf_quality_metrics.png` in the `evaluation` directory.

### Running Comprehensive Evaluation

To perform a detailed parameter sweep across stability, environment, and ECC types:

```bash
python evaluation/evaluate_comprehensive.py
```

This generates several plots and a CSV file (`evaluation/comprehensive_evaluation_results.csv`) detailing the results.

### Running BCH Robustness Verification

To test and compare different BCH error correction configurations:

```bash
python evaluation/verify_bch_robustness.py
```

This will test multiple BCH configurations (with different error correction capabilities) under various aging factors and generate a comparison plot saved as `bch_robustness_comparison.png`.

### Entropy Analysis

To analyze the entropy reduction caused by enabling ECC:

```bash
python evaluation/analyze_entropy.py
```

### Running Tests

To verify the correctness of the system, you can run the unit tests:

```bash
python test/test_cell.py
# Add other test files as needed
```

## Project Structure

```
.
├── model/
│   ├── cell.py              # SRAMCell class (core physics model)
│   ├── sram.py              # SRAMArray class (array of cells)
│   ├── sram_based_puf.py    # SRAM_PUF class (PUF logic)
│   └── ecc/
│       └── ecc.py           # HammingECC and BCHECC classes
├── evaluation/
│   ├── evaluate_puf.py      # Script to evaluate basic PUF quality metrics
│   ├── evaluate_comprehensive.py # Comprehensive evaluation script
│   ├── analyze_entropy.py   # Entropy analysis script
│   ├── verify_bch_robustness.py  # Script to test BCH configurations
│   └── ... (generated plots)
├── test/
│   ├── test_cell.py         # Unit tests for SRAMCell
│   └── ...
├── requirements.txt         # Python dependencies
└── README.md                # This file
```
