import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add the parent directory to sys.path to import the model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.cell import SRAMCell

def generate_s_init_distribution(num_samples=10000):
    """Generates and plots the distribution of S_init (stability) from the SRAMCell model."""
    
    s_init_values = []
    
    print(f"Generating {num_samples} SRAMCell samples...")
    for _ in range(num_samples):
        cell = SRAMCell()
        s_init_values.append(cell.stability)
        
    s_init_values = np.array(s_init_values)
    
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.hist(s_init_values, bins=50, color='skyblue', edgecolor='black', alpha=0.7, density=True, label='Simulated Samples')
    
    # Try to plot the theoretical Beta(8, 2) distribution for comparison if scipy is available
    try:
        from scipy.stats import beta
        x = np.linspace(0, 1, 100)
        y = beta.pdf(x, 8, 2)
        plt.plot(x, y, 'r-', linewidth=2, label='Theoretical Beta(8, 2)')
    except ImportError:
        print("Scipy not found, skipping theoretical distribution plot.")
    
    plt.title('Distribution of Initial Stability ($S_{init}$) in SRAM Cell Model')
    plt.xlabel('Stability ($S_{init}$)')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_path = os.path.join(os.path.dirname(__file__), 's_init_distribution.png')
    plt.savefig(output_path)
    print(f"Distribution plot saved to {output_path}")
    
    # Calculate and print statistics
    mean_val = np.mean(s_init_values)
    std_val = np.std(s_init_values)
    print(f"Mean: {mean_val:.4f}")
    print(f"Std Dev: {std_val:.4f}")

if __name__ == "__main__":
    generate_s_init_distribution()
