# Documentation: `evaluate_burnin_ecc.py`

This document explains the functionality of the `evaluate_burnin_ecc.py` script, focusing on how the Bit Error Rate (BER) is calculated and the overall workflow of the evaluation.

## 1. BER Calculation Logic

The Bit Error Rate (BER) is calculated by the function `evaluate_ber`. It measures the reliability of the PUF response by comparing noisy responses generated under specific environmental conditions (temperature, voltage) against the "golden" enrollment response.

### Calculation Steps

1.  **Golden Response Retrieval**:
    *   The script retrieves the `puf.puf_response`. This is the "golden" response generated during the PUF's initialization (enrollment phase) at nominal conditions (25°C, 1.0V).
    *   If **Burn-in** is enabled, this golden response only contains the bits from cells identified as "stable" during the burn-in phase. Unstable cells are masked out.

2.  **Sampling Loop**:
    *   The script generates `samples` (default: 20) number of noisy responses for the specified `temp` (temperature) and `volt` (voltage ratio).
    *   `response = puf.get_response(temperature=temp, voltage_ratio=volt)`
    *   **Note on ECC**: If ECC is enabled for the PUF instance, `get_response` returns the *corrected* response. If ECC is disabled, it returns the raw noisy response.

3.  **Error Counting**:
    *   For each sample, the script compares the noisy `response` with the `golden` response bit by bit.
    *   It counts the number of mismatching bits: `np.sum(response != golden)`.

4.  **Final Calculation**:
    *   The total number of errors across all samples is summed up.
    *   The total number of bits processed is calculated as: `total_bits = len(golden) * samples`.
    *   **BER Formula**:
        $$ \text{BER} = \frac{\text{Total Errors}}{\text{Total Bits}} $$

### Code Snippet Reference
```python
def evaluate_ber(puf, temp, volt, samples=20):
    # ...
    golden = puf.puf_response
    # ...
    for _ in range(samples):
        response = puf.get_response(temperature=temp, voltage_ratio=volt)
        errors += np.sum(response != golden)
        total_bits += len(golden)
    # ...
    return errors / total_bits
```

## 2. Script Functionality & Workflow

The main goal of this script is to compare the robustness of different PUF configurations (combinations of Burn-in and ECC) under varying environmental conditions.

### Configurations Tested
The script evaluates 6 distinct configurations:
1.  **No Burn-in, No ECC**: Baseline raw PUF performance.
2.  **Burn-in, No ECC**: PUF with unstable bits masked out (should have lower BER than baseline).
3.  **No Burn-in, Hamming**: Raw PUF protected by Hamming ECC (Single Error Correction).
4.  **Burn-in, Hamming**: Burn-in PUF protected by Hamming ECC.
5.  **No Burn-in, BCH (t=5)**: Raw PUF protected by BCH ECC (corrects up to 5 errors).
6.  **Burn-in, BCH (t=5)**: Burn-in PUF protected by BCH ECC.

### Experiment Workflow

1.  **Initialization**:
    *   It creates 10 independent PUF instances for each of the 6 configurations.
    *   This ensures the results are statistically significant and not biased by a single "lucky" or "unlucky" PUF instance.

2.  **Experiment 1: Temperature Sweep**:
    *   **Variable**: Temperature (-20°C to 125°C).
    *   **Fixed**: Voltage Ratio (1.0).
    *   **Metric**: Average BER across all 10 PUF instances for each temperature point.

3.  **Experiment 2: Voltage Sweep**:
    *   **Variable**: Voltage Ratio (0.8x to 1.2x).
    *   **Fixed**: Temperature (25°C).
    *   **Metric**: Average BER across all 10 PUF instances for each voltage point.

4.  **Visualization**:
    *   The script generates a plot with two subplots:
        *   **Left**: BER vs. Temperature.
        *   **Right**: BER vs. Voltage Ratio.
    *   The Y-axis is plotted on a logarithmic scale (`log`) to better visualize the differences in low BER values.
    *   Output file: `evaluation/result/burnin_ecc_comparison.png`.

## 3. Interpretation of Results

*   **Ideal Outcome**: The "Burn-in, BCH" configuration is expected to have the lowest BER because it combines two reliability enhancement techniques:
    *   **Burn-in**: Removes the most unstable bits physically.
    *   **ECC**: Corrects remaining random bit flips.
*   **Crossing Lines**: If "Burn-in" performs worse than "No Burn-in" in some cases (specifically with ECC), it might be due to:
    *   **Reduced Block Size**: Burn-in reduces the number of available bits. For block codes like BCH, a shorter block size with the same error capability might have different properties or initialization constraints.
    *   **Miscorrection**: If the raw BER is extremely high (e.g., at 125°C), ECC might fail and introduce *more* errors (miscorrection), especially if the code parameters were not optimized for the post-burn-in length.
