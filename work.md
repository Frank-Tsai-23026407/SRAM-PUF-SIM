# SRAM-PUF Simulator: A Step-by-Step Implementation Guide

This document provides a recommended workflow for building a software-based SRAM-PUF simulator using Python. The simulator will model the startup behavior of SRAM cells and evaluate the quality of the generated PUF responses.

## Prerequisites

- Python 3.x
- NumPy: For numerical operations and array management.
- Matplotlib: For visualizing results (optional but recommended).

## Step 1: Environment Setup

First, set up a virtual environment to manage project dependencies.

```bash
# Create a virtual environment
python -m venv sram_puf_env

# Activate the environment
# On Windows
sram_puf_env\Scripts\activate
# On macOS and Linux
source sram_puf_env/bin/activate

# Install required libraries
pip install numpy matplotlib
```

## Step 2: Modeling a Single SRAM Cell

The startup value of an SRAM cell is determined by the random mismatch in the threshold voltages of its cross-coupled inverters. We can model this mismatch using a normal distribution. A positive difference might result in a '1', while a negative difference results in a '0'.

**`cell_model.py`**
```python
import numpy as np

def simulate_sram_cell(mu=0, sigma=1):
    """
    Simulates the startup value of a single SRAM cell.

    The startup behavior is modeled by sampling from a normal distribution,
    representing the threshold voltage mismatch. A positive value is mapped to 1,
    and a negative value is mapped to 0.

    Args:
        mu (float): The mean of the normal distribution (ideal is 0).
        sigma (float): The standard deviation of the normal distribution.

    Returns:
        int: The simulated startup value (0 or 1).
    """
    mismatch = np.random.normal(mu, sigma)
    return 1 if mismatch > 0 else 0
```

## Step 3: Simulating the SRAM Array

An SRAM PUF is an array of these cells. We can simulate the entire array by creating a 2D matrix of startup values.

**`puf_simulator.py`**
```python
import numpy as np
from cell_model import simulate_sram_cell

def generate_startup_pattern(rows, cols):
    """
    Generates the initial startup pattern for an SRAM array.

    Args:
        rows (int): The number of rows in the SRAM array.
        cols (int): The number of columns in the SRAM array.

    Returns:
        np.ndarray: A 2D NumPy array representing the PUF's initial response.
    """
    puf_response = np.zeros((rows, cols), dtype=int)
    for i in range(rows):
        for j in range(cols):
            puf_response[i, j] = simulate_sram_cell()
    return puf_response

# Example: Generate a 64x128 bit PUF response
puf_instance = generate_startup_pattern(64, 128)
print("Generated PUF Response:")
print(puf_instance)
```

## Step 4: Implementing Challenge-Response Pairs (CRPs)

A challenge determines which bits of the PUF response are selected to form the final output. A simple approach is to use the challenge to select specific rows or columns.

**`puf_simulator.py` (continued)**
```python
def get_response(puf_instance, challenge):
    """
    Generates a response for a given challenge.

    This simple implementation uses the challenge as a seed to select a
    random subset of PUF cells.

    Args:
        puf_instance (np.ndarray): The SRAM startup pattern.
        challenge (int): An integer challenge used to seed the RNG.

    Returns:
        np.ndarray: The PUF response (a 1D array of bits).
    """
    np.random.seed(challenge)
    response_length = 128  # Example response length
    rows, cols = puf_instance.shape

    # Generate unique random indices
    indices = np.random.choice(rows * cols, size=response_length, replace=False)

    # Flatten the PUF instance and select bits
    response = puf_instance.flatten()[indices]

    return response

# Example: Get a response for challenge 123
challenge = 123
response = get_response(puf_instance, challenge)
print(f"\nResponse for challenge {challenge}:")
print(response)
```

## Step 5: Evaluating PUF Quality Metrics

To assess the quality of the simulated PUF, we evaluate its uniformity, uniqueness, and reliability.

**`puf_metrics.py`**
```python
import numpy as np

def calculate_uniformity(puf_response):
    """
    Calculates the uniformity of a PUF response.
    Ideal uniformity is 50%.
    """
    return np.mean(puf_response) * 100

def calculate_hamming_distance(resp1, resp2):
    """
    Calculates the Hamming distance between two responses.
    """
    return np.sum(resp1 != resp2)

def evaluate_uniqueness(puf_instances):
    """
    Evaluates uniqueness by calculating the average inter-chip Hamming distance.
    Ideal uniqueness is 50%.
    """
    num_instances = len(puf_instances)
    distances = []
    for i in range(num_instances):
        for j in range(i + 1, num_instances):
            dist = calculate_hamming_distance(puf_instances[i], puf_instances[j])
            distances.append(dist / puf_instances[i].size)

    return np.mean(distances) * 100

def introduce_noise(puf_response, noise_level=0.05):
    """
    Simulates environmental noise by flipping a percentage of bits.
    """
    noisy_response = puf_response.copy().flatten()
    num_bits_to_flip = int(noisy_response.size * noise_level)

    flip_indices = np.random.choice(noisy_response.size, size=num_bits_to_flip, replace=False)
    noisy_response[flip_indices] = 1 - noisy_response[flip_indices]

    return noisy_response.reshape(puf_response.shape)

def evaluate_reliability(puf_instance, noise_level=0.05, num_evaluations=100):
    """
    Evaluates reliability by measuring the intra-chip Hamming distance under noise.
    Ideal reliability is 100% (0% bit flips).
    """
    original_response = puf_instance.flatten()
    distances = []
    for _ in range(num_evaluations):
        noisy_version = introduce_noise(puf_instance, noise_level).flatten()
        dist = calculate_hamming_distance(original_response, noisy_version)
        distances.append(dist / original_response.size)

    avg_bit_error_rate = np.mean(distances)
    return (1 - avg_bit_error_rate) * 100

# Example Usage:
# 1. Uniformity
uniformity = calculate_uniformity(puf_instance)
print(f"Uniformity: {uniformity:.2f}%")

# 2. Uniqueness (requires multiple PUF instances)
num_devices = 50
pufs = [generate_startup_pattern(64, 128) for _ in range(num_devices)]
uniqueness = evaluate_uniqueness(pufs)
print(f"Uniqueness: {uniqueness:.2f}%")

# 3. Reliability
reliability = evaluate_reliability(puf_instance, noise_level=0.1)
print(f"Reliability: {reliability:.2f}%")
```

## Step 6: Advanced Features (Next Steps)

- **Helper-Data Algorithms:** Implement algorithms like Fuzzy Extractors to generate stable cryptographic keys from noisy PUF responses.
- **Aging and Environmental Effects:** Model how temperature, voltage fluctuations, and device aging affect the PUF's reliability over time.
- **Machine Learning Attacks:** Simulate and test the PUF's resilience against machine learning attacks that attempt to model and predict its behavior.

This guide provides a foundational workflow for creating a versatile SRAM-PUF simulator. You can extend it by incorporating more complex models and analysis techniques based on the latest research.
