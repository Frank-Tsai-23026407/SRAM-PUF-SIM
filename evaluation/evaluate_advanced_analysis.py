import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from scipy import stats

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.sram_based_puf import SRAM_PUF

def calculate_min_entropy(data):
    """Calculates the Min-Entropy of a binary array.
    
    Min-entropy is a worst-case estimate of entropy, often used in security.
    H_min = -log2(max(p_0, p_1))
    """
    p1 = np.mean(data)
    p0 = 1.0 - p1
    max_prob = max(p0, p1)
    if max_prob == 0:
        return 0.0
    return -np.log2(max_prob)

def calculate_spatial_autocorrelation(data_2d):
    """Calculates the 2D spatial autocorrelation of the SRAM array.
    
    This checks if a cell's value is correlated with its neighbors.
    """
    rows, cols = data_2d.shape
    if rows < 2 or cols < 2:
        return 0.0
    
    # Calculate correlation with immediate neighbors (right and down)
    # Horizontal correlation
    h_corr = np.corrcoef(data_2d[:, :-1].flatten(), data_2d[:, 1:].flatten())[0, 1]
    
    # Vertical correlation
    v_corr = np.corrcoef(data_2d[:-1, :].flatten(), data_2d[1:, :].flatten())[0, 1]
    
    return (h_corr + v_corr) / 2.0

def analyze_bias_map(num_pufs=100, rows=64, cols=64):
    """Generates a bias map showing the probability of each cell being 1 across multiple PUFs.
    
    This helps identify if certain physical locations are systematically biased.
    """
    print(f"Generating Bias Map from {num_pufs} PUF instances...")
    accumulated_response = np.zeros((rows, cols))
    
    for _ in range(num_pufs):
        puf = SRAM_PUF(num_cells=rows*cols)
        # Reshape 1D response to 2D
        resp = puf.puf_response.reshape((rows, cols))
        accumulated_response += resp
        
    prob_map = accumulated_response / num_pufs
    
    # Plotting
    plt.figure(figsize=(10, 8))
    plt.imshow(prob_map, cmap='RdBu', vmin=0, vmax=1)
    plt.colorbar(label='Probability of being 1')
    plt.title(f'SRAM Cell Bias Map ({num_pufs} instances)')
    plt.xlabel('Column Index')
    plt.ylabel('Row Index')
    
    output_path = 'evaluation/result/bias_map.png'
    plt.savefig(output_path)
    print(f"Bias map saved to {output_path}")
    
    return prob_map

def main():
    rows, cols = 64, 64
    num_cells = rows * cols
    
    print("--- Advanced PUF Analysis ---")
    
    # 1. Single PUF Analysis
    puf = SRAM_PUF(num_cells=num_cells)
    response = puf.puf_response
    response_2d = response.reshape((rows, cols))
    
    # Min-Entropy
    min_ent = calculate_min_entropy(response)
    print(f"Min-Entropy: {min_ent:.4f} bits/cell")
    
    # Spatial Autocorrelation
    spatial_corr = calculate_spatial_autocorrelation(response_2d)
    print(f"Spatial Autocorrelation: {spatial_corr:.4f} (should be close to 0)")
    
    # 2. Population Analysis (Bias Map)
    prob_map = analyze_bias_map(num_pufs=100, rows=rows, cols=cols)
    
    # Analyze the distribution of biases
    # Ideally, the distribution of probabilities should be centered at 0.5
    plt.figure()
    plt.hist(prob_map.flatten(), bins=30, alpha=0.7, color='green', edgecolor='black')
    plt.title('Distribution of Cell Biases')
    plt.xlabel('Probability of being 1')
    plt.ylabel('Count')
    plt.axvline(0.5, color='red', linestyle='dashed', linewidth=1)
    plt.savefig('evaluation/result/bias_distribution.png')
    print("Bias distribution plot saved to evaluation/result/bias_distribution.png")

if __name__ == "__main__":
    main()
