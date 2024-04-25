import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import ScalarFormatter
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data')
ACROBAT_DIR = os.path.join(DATA_DIR, 'acrobat', 'transects', 'processed', 'processed_dataset.csv')
SAVE_DIR =  os.path.join(SCRIPT_DIR, '..', 'visualization', 'depth_distributions')
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

print("Loading data...")
data = pd.read_csv(ACROBAT_DIR)
print("Data loaded successfully.")

bins = [0, 2, 4, 6, 8, 10]
labels = [f'{int(bins[i])}-{int(bins[i+1])} m' for i in range(len(bins)-1)]
data['depth_category'] = pd.cut(data['depth'], bins=bins, labels=labels, right=False)

variables_to_plot = {
    'temp': 'Temperature (°C)',
    'salinity': 'Salinity (psu)',
    'turbidity': 'Turbidity (NTU)',
    'chlor_a': 'Chlorophyll-a (µg/L)',
    'ox_sat': 'Oxygen Saturation (%)',
    'density': 'Density (kg/m³)'
}

def create_and_save_plots(data, variable, unit, SAVE_DIR):
    plt.figure(figsize=(30, 10))
    ax = sns.boxplot(data=data, x='transect_id', y=variable, hue='depth_category', palette='viridis')
    plt.title(f'{variable.capitalize()} Distribution Across Transects and Depth', fontsize=20)
    plt.xlabel('Transect ID', fontsize=16)
    plt.ylabel(unit, fontsize=16)
    plt.legend(title='Depth Category', loc='best', fancybox=True, shadow=False, fontsize=14, title_fontsize=16)
    plt.grid(True)
    
    if variable == 'density':  # Check if the variable is 'density'
        ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))  # Use ScalarFormatter to avoid scientific notation
    
    plot_path = os.path.join(SAVE_DIR, f'{variable}.png')
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.savefig(plot_path, dpi=500, bbox_inches='tight')
    plt.close()

sns.set_context("talk")

for variable, unit in variables_to_plot.items():
    create_and_save_plots(data, variable, unit, SAVE_DIR)
    print(f"Completed plotting for {variable}.")