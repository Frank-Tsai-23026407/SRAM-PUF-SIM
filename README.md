# SRAM-PUF Simulator

This project provides a Python-based simulation environment for SRAM-based Physical Unclonable Functions (PUFs). It allows for the modeling and analysis of SRAM start-up behavior, and includes features to evaluate PUF quality metrics like uniformity, uniqueness, and reliability under simulated aging conditions. The simulator also implements a Hamming code for error correction to enhance the PUF's stability.

## About PUFs

A Physical Unclonable Function (PUF) is a physical entity that leverages inherent randomness in manufacturing processes to create a unique and unclonable identifier for a physical object, typically an integrated circuit. A PUF is easy to evaluate but hard to predict or duplicate, making it suitable for applications such as secure key generation, authentication, and anti-counterfeiting.

## SRAM-based PUFs

SRAM-based PUFs utilize the random initial state of SRAM cells upon power-up. Each SRAM cell has a preferred state (0 or 1) due to minor manufacturing variations. This pattern of 0s and 1s is unique to each chip and can be used as a digital "fingerprint."

## Features

- **SRAM Cell and Array Simulation:** Models individual SRAM cells and arrays, including the simulation of aging effects.
- **Error Correction:** Implements a Hamming code to correct single-bit errors in PUF responses, improving reliability.
- **PUF Quality Evaluation:** Includes a script to calculate and plot key PUF quality metrics:
    - **Uniformity:** The balance of 0s and 1s in a PUF response.
    - **Uniqueness:** The difference between responses from multiple PUF instances.
    - **Reliability:** The stability of a PUF's response over time (simulated by an aging factor).
- **Testing:** Comes with a unit test to verify the correctness of the Hamming code implementation.

## Getting Started

### Prerequisites

- Python 3.x
- NumPy
- Matplotlib

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
    pip install numpy matplotlib
    ```

## Usage

### Running the Evaluation

To evaluate the quality of the simulated PUF and generate a plot of the results, run the `evaluate_puf.py` script:

```bash
python evaluation/evaluate_puf.py
```

This will run a series of simulations with varying aging factors and save a plot named `puf_quality_metrics.png` in the `evaluation` directory.

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
│   ├── cell.py           # SRAMCell class
│   ├── sram.py           # SRAM class (array of cells)
│   └── sram_based_puf.py # SRAM_PUF and HammingECC classes
├── evaluation/
│   ├── evaluate_puf.py   # Script to evaluate PUF quality
│   └── puf_quality_metrics.png # Example output plot
├── test/
│   └── test_puf.py       # Unit test for the Hamming ECC
└── README.md             # This file
```
