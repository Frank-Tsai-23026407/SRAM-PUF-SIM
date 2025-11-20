import numpy as np
from model.sram_based_puf import SRAM_PUF
from model.ecc.ecc import HammingECC, BCHECC

def calculate_entropy(data):
    """Calculates the Shannon entropy of a binary array."""
    prob = np.sum(data) / len(data)
    if prob == 0 or prob == 1:
        return 0
    return -prob * np.log2(prob) - (1 - prob) * np.log2(1 - prob)

def analyze_puf_entropy(rows, cols, ecc_class=None, **ecc_args):
    """Analyzes the entropy of a PUF with and without ECC."""

    # Create a PUF without ECC to get the raw response
    puf_no_ecc = SRAM_PUF(rows=rows, cols=cols, ecc=None)
    raw_response = puf_no_ecc.puf_response
    entropy_no_ecc = calculate_entropy(raw_response)

    # Create a PUF with the specified ECC
    if ecc_class:
        ecc_instance = ecc_class(data_len=rows * cols, **ecc_args)
        puf_with_ecc = SRAM_PUF(rows=rows, cols=cols, ecc=ecc_instance)

        # The helper data reduces the entropy
        if ecc_class == BCHECC:
            helper_data_size = len(puf_with_ecc.helper_data) * 8
        elif ecc_class == HammingECC:
            helper_data_size = len(puf_with_ecc.helper_data)
        else:
            helper_data_size = 0 # Should not happen

        entropy_reduction = helper_data_size / (rows*cols)
        entropy_with_ecc = entropy_no_ecc - entropy_reduction
    else:
        entropy_with_ecc = None
        entropy_reduction = 0

    return entropy_no_ecc, entropy_with_ecc, entropy_reduction


if __name__ == "__main__":
    rows, cols = 64, 64

    # Analysis without ECC
    entropy_no_ecc, _, _ = analyze_puf_entropy(rows, cols)
    print(f"Entropy without ECC: {entropy_no_ecc:.4f}")

    # Analysis with Hamming ECC
    ent_ne, ent_we_h, red_h = analyze_puf_entropy(rows, cols, HammingECC)
    print(f"Entropy with Hamming ECC: {ent_we_h:.4f} (Reduction: {red_h:.4f})")

    # Analysis with BCH ECC
    ent_ne, ent_we_b, red_b = analyze_puf_entropy(rows, cols, BCHECC, t=5)
    print(f"Entropy with BCH ECC (t=5): {ent_we_b:.4f} (Reduction: {red_b:.4f})")
