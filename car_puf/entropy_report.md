# Automotive PUF Entropy Analysis Report

## 1. Introduction
This report analyzes the trade-offs between reliability and entropy in the `CarPUF` implementation. Automotive applications require high reliability (low Bit Error Rate), achieved through:
1.  **Unstable Cell Masking (Burn-In):** Removing cells that flip under stress.
2.  **Strong Error Correction (ECC):** Adding redundancy to correct remaining errors.

Both methods reduce the **Effective Entropy** (usable secret bits) of the PUF. This analysis quantifies that loss.

## 2. Methodology
We simulated a `CarPUF` with **1024 raw SRAM cells** under various configurations:
-   **Burn-In Rounds:** 0 (No masking), 5, 10, 20 (Strict masking).
-   **ECC Capability ($t$):** Number of correctable errors (BCH code).

### Metrics
-   **Stable Cells:** Count of cells remaining after burn-in.
-   **Mask Loss:** $N_{total} - N_{stable}$.
-   **Helper Data Leakage:** Information revealed by ECC parity bits (public data).
-   **Effective Entropy:** $Entropy_{stable} - Leakage$.

## 3. Results Summary

The following table shows the degradation of entropy as reliability requirements increase (Data from 1024 raw cells).

| Burn-In (Rounds) | ECC ($t$) | Stable Cells (Avg) | Mask Loss | ECC Leakage (bits) | **Effective Entropy (bits)** | Efficiency (bits/cell) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **0 (Baseline)** | 5 | 1024 | 0 | 56 | **966.8** | 0.94 |
| 0 | 20 | 1024 | 0 | 224 | **799.6** | 0.78 |
| **5 (Standard)** | 5 | ~265 | ~759 | 48 | **216.3** | 0.21 |
| 5 | 20 | ~270 | ~754 | 184 | **85.9** | 0.08 |
| **10 (Strict)** | 5 | ~90 | ~934 | 40 | **48.2** | 0.05 |
| 10 | 20 | ~76 | ~948 | 160 | **Negative (Failed)** | < 0 |
| **20 (Extreme)** | All | < 15 | > 1000 | > 30 | **Negative (Failed)** | < 0 |

*(Note: Negative entropy indicates the ECC leakage exceeds the information content of the remaining stable cells, meaning the system is insecure or mathematically impossible to initialize properly.)*

## 4. Analysis & Intuition

### 4.1 The Cost of Stability (Masking)
The most significant entropy loss comes from **Burn-In Masking**.
-   At **5 rounds** of burn-in (at 125°C/1.2V), we lose nearly **75%** of the cells. This is because the simulated cells have a realistic stability distribution, and the stress test is very aggressive.
-   At **10+ rounds**, we lose **>90%** of cells.
-   **Intuition:** The "burn-in" process is a filter. We are asking for cells that are "perfectly" stable under extreme noise. In a Gaussian distribution of stability, only the tail ends (very strong 0s or 1s) survive. We discard the majority of "average" cells.

### 4.2 The Cost of Correction (ECC)
Increasing ECC capability ($t$) linearly increases leakage.
-   Going from $t=5$ to $t=20$ roughly quadruples the helper data size.
-   When stable cells are few (e.g., after strict burn-in), the ECC overhead can easily exceed the raw data size.
-   **Intuition:** You cannot correct more errors than you have redundancy. If you have 90 stable bits but need to correct 20 errors using BCH, you might need ~160 bits of parity. Since $160 > 90$, you simply don't have enough entropy to support that level of correction.

## 5. Recommendations for Automotive Use

1.  **Over-Provisioning:** To achieve a secure 128-bit key with automotive reliability (Burn-in=5, ECC $t=10$), the results suggest we get ~0.17 bits/cell.
    -   **Requirement:** To get 128 bits of entropy, we need $128 / 0.17 \approx 752$ cells.
    -   **Safety Margin:** We should allocate **1024 to 2048 cells** for a single 128-bit key to be safe.

2.  **Tuning Burn-In:**
    -   20 rounds is likely too strict for the current cell model, leaving almost nothing.
    -   **5 rounds** appears to be the "sweet spot" where we filter the worst cells but keep enough (~25%) to form a key.

3.  **Tuning ECC:**
    -   After masking, the remaining cells are very stable. We might not *need* $t=20$ for the masked subset.
    -   A lower $t$ (e.g., $t=5$ or $t=10$) on the *masked* population is likely sufficient and preserves more entropy.

## 6. Conclusion
Building a `CarPUF` involves a massive trade-off. To guarantee operation at 125°C for 15 years, we sacrifice nearly **80-90%** of the raw SRAM capacity. Designers must account for this by significantly over-provisioning the SRAM array size compared to consumer-grade PUFs.
