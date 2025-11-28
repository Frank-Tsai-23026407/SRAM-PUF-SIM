# Evaluation Scripts Documentation

This directory contains scripts for evaluating the performance, robustness, and entropy of the SRAM PUF model.

## Script Descriptions

| Script Name | Status | Description |
| :--- | :--- | :--- |
| `analyze_entropy.py` | **Active** | Calculates the Shannon entropy of PUF responses. Supports analysis of raw PUF entropy and effective entropy after ECC helper data leakage. |
| `evaluate_burnin_ecc.py` | **Active** | Evaluates the Bit Error Rate (BER) of PUF configurations (with/without Burn-in, with/without ECC) across different temperatures and voltages. Generates `burnin_ecc_comparison.png`. |
| `evaluate_comprehensive.py` | **Active** | A comprehensive evaluation suite that iterates over Stability parameters, Environmental conditions (Voltage, Temp), and Storage Patterns. Generates detailed CSV results and multiple plots (`robustness_vs_stability.png`, `entropy_vs_ecc.png`, etc.). |
| `evaluate_puf.py` | **Active** | Simulates aging cycles to measure and plot PUF quality metrics: Reliability, Uniformity, and Uniqueness over time. Generates `puf_quality_metrics.png`. |
| `evaluate_advanced_analysis.py` | **Active** | Performs advanced analysis including Min-Entropy calculation, Spatial Autocorrelation, and Bias Map generation. Generates `bias_map.png` and `bias_distribution.png`. |
| `evaluate_car_entropy.py` | **Active** | Specialized entropy analysis for Automotive PUF, accounting for mask loss due to strict burn-in requirements. |
| `demo_car_puf.py` | **Active** | Demonstrates the full lifecycle of an Automotive PUF: Enrollment (Burn-in), Temperature Testing, Aging Simulation, and Health Monitoring. |
| `verify_bch_robustness.py` | **Active** | Specifically tests and compares the robustness of BCH vs. Hamming ECC codes under simulated bit-flip probabilities (aging factors). Prints an efficiency summary and plots `ecc_robustness_comparison.png`. |
| `reproduce_issue.py` | **Debug** | A script designed to investigate specific issues with BCH ECC behavior, particularly cases where ECC might increase errors. Useful for debugging ECC logic. |
| `puf_with_burn_in_robustness.py` | **Empty** | Currently empty. Recommended for deletion or implementation. |

## Usage

Most scripts can be run directly from the command line:

```bash
python evaluation/evaluate_comprehensive.py
```

Ensure you are in the root `SRAM-PUF-SIM` directory so that python path imports work correctly.

## Proposed New Analyses

Based on the current coverage, the following additional analyses are recommended:

1.  **Machine Learning Attack Simulation**:
    *   **Goal**: Test the PUF's resistance to modeling attacks.
    *   **Method**: Collect Challenge-Response Pairs (CRPs) and train a simple ML model (e.g., SVM or Neural Net) to predict responses.
    *   **File**: `evaluate_ml_attack.py` (To be created)

2.  **Advanced Aging Simulation**:
    *   **Goal**: Simulate long-term aging effects beyond simple burn-in.
    *   **Method**: Use the `storage_pattern` parameter more extensively to simulate years of operation under different workloads.

3.  **NIST Randomness Test Suite Integration**:
    *   **Goal**: Verify the randomness of the PUF output using standard statistical tests.
    *   **Method**: Export PUF data to a format compatible with NIST SP 800-22 tests.
