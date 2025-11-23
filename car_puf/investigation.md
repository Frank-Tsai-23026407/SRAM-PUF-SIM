# Automotive SRAM PUF Investigation

## 1. Introduction
This document outlines the investigation and requirements for deploying SRAM-based Physical Unclonable Functions (PUFs) in automotive environments. Unlike consumer electronics, automotive components must adhere to strict safety (ISO 26262) and reliability (AEC-Q100) standards, operating correctly for 10-15 years under harsh conditions.

## 2. Challenges in Automotive Environment

### 2.1 Temperature Range
Automotive Grade 1 requires operation from -40°C to +125°C (Grade 0 goes up to +150°C).
- **Impact on SRAM PUF**: Thermal noise increases with temperature. A cell stable at 25°C might flip at 125°C. The "Noise Margin" decreases, leading to higher bit error rates (BER).

### 2.2 Aging (NBTI/HCI)
Over a 15-year lifespan, transistors degrade.
- **NBTI (Negative Bias Temperature Instability)**: Affects PMOS transistors when held at "0" (or "1", depending on structure) for long periods. This increases the threshold voltage ($V_{th}$), potentially changing the cell's preferred power-up state.
- **Impact on PUF**: A "stable 0" might eventually become unstable or flip to a "1" permanently.

### 2.3 Reliability & Safety
- **Bit Error Rate (BER)**: Raw SRAM PUFs have non-zero BER. Automotive crypto keys must have a BER of effectively 0.
- **Functional Safety (ISO 26262)**: The system must detect faults. If the PUF fails to reconstruct the key, it must report an error rather than outputting a wrong key (Availability vs. Integrity).

## 3. Reliability Enhancement Strategies

To ensure a robust `CarPUF`, we employ a multi-layered approach:

### 3.1 Unstable Cell Masking (Pre-Processing)
During the **Enrollment Phase** (manufacturing), we identify cells that are unstable.
- **Method**: "Burn-in" testing. Power up the device multiple times at high temperature (e.g., 125°C) and voltage stress.
- **Action**: Create a mask to ignore cells that flip during these tests. Only the most robust cells are used for key generation.

### 3.2 Strong Error Correction Codes (ECC)
Standard Hamming codes (correct 1 bit) are insufficient for the high-noise automotive environment.
- **Solution**: BCH (Bose-Chaudhuri-Hocquenghem) codes or Repetition Codes + BCH.
- **Requirement**: The ECC must handle a raw BER of up to 15-20% (worst-case end-of-life hot temperature).

### 3.3 Anti-Aging Protocols
- **Method**: Avoid leaving the SRAM in the same state for years.
- **Implementation**: If the SRAM is not in use, power it down or write random patterns / inverse patterns to balance the stress on transistors.

### 3.4 Runtime Health Monitoring (Safety)
- **Method**: Consistency checks.
- **Implementation**: Periodically regenerate the key (or a test vector) and verify the syndrome. If the number of corrected errors approaches the ECC limit, signal a warning (Predictive Maintenance).

## 4. Implementation Plan (`CarPUF` Class)

We will implement a Python class `CarPUF` that simulates these strategies.

### 4.1 Features
1.  **Strict Enrollment**: Enforce high-temperature burn-in during initialization.
2.  **Simulation of Harsh Conditions**: Allow `get_response` to accept extreme temperatures (-40 to 150).
3.  **Aging Simulation**: Methods to simulate year-by-year degradation.
4.  **Health Monitor**: A method `check_health()` that returns the current raw bit error rate relative to the golden key.

### 4.2 Code Structure
The `CarPUF` will wrap the existing `SRAM_PUF` logic but effectively "hardcode" the reliability settings required for automotive use.

```python
class CarPUF:
    def __init__(self, num_cells):
        # Enforce burn-in at 125°C for stability masking
        self.puf = SRAM_PUF(..., burn_in_rounds=10, burn_in_temp=125)

    def drive_cycle(self, duration_hours, temp_profile):
        # Simulate aging based on usage
        ...
```
