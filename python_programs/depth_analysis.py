import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np

# Define directories and paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'acrobat', 'transects', 'processed')
ACROBAT_DIR = os.path.join(DATA_DIR, 'processed_dataset.csv')

CSV_SAVE_DIR = os.path.join(DATA_DIR)
if not os.path.exists(CSV_SAVE_DIR):
    os.makedirs(CSV_SAVE_DIR)
CSV_SAVE_PATH = os.path.join(CSV_SAVE_DIR, 'oc_params_by_depth.csv')

VISUAL_SAVE_DIR = os.path.join(SCRIPT_DIR, '..', 'visualization', 'depth_distributions')
if not os.path.exists(VISUAL_SAVE_DIR):
    os.makedirs(VISUAL_SAVE_DIR)

# Load the dataset
print("Loading data...")
data = pd.read_csv(ACROBAT_DIR)
print("Data loaded successfully.")

# Define the depth bins and labels
depth_bins = [0, 2, 4, 6, 8, 10]
depth_labels = [f'{int(depth_bins[i])}-{int(depth_bins[i+1])} m' for i in range(len(depth_bins)-1)]
data['depth_range'] = pd.cut(data['depth'], bins=depth_bins, labels=depth_labels, right=False)

# Add an overall range 0-10
data['overall_range'] = '0-10'

# Define parameters to plot and their units
variables_to_plot = {
    'temp': 'Temperature (°C)',
    'salinity': 'Salinity (psu)',
    'turbidity': 'Turbidity (NTU)',
    'chlor_a': 'Chlorophyll-a (µg/L)',
    'do': 'Dissolved Oxygen (mg/L)',
    'density': 'Density (kg/m³)'
}

# Function to create and save box plots
def create_and_save_plots(data, variable, unit, save_dir):
    plt.figure(figsize=(25, 15))
    ax = sns.boxplot(data=data, x='transect_id', y=variable, hue='depth_range', palette='viridis')
    plt.title(f'{variable.capitalize()} Distribution Across Transects and Depth', fontsize=26)
    plt.xlabel('Transect ID', fontsize=25)
    plt.ylabel(unit, fontsize=25)
    plt.legend(title='Depth Category', loc='best', fancybox=True, shadow=False, fontsize=20, title_fontsize=22)
    plt.grid(True)
    
    if variable == 'density':
        ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    
    plot_path = os.path.join(save_dir, f'{variable}.png')
    plt.xticks(fontsize=24)
    plt.yticks(fontsize=24)
    plt.savefig(plot_path, dpi=500, bbox_inches='tight')
    plt.close()

# Generate plots for each variable
sns.set_context("talk")
for variable, unit in variables_to_plot.items():
    create_and_save_plots(data, variable, unit, VISUAL_SAVE_DIR)
    print(f"Completed plotting for {variable}.")

# Calculate and save average parameters by depth
rows_list = []
grouped_by_depth = data.groupby('depth_range', observed=True)  # Explicitly specify observed=True
for depth_range, group in grouped_by_depth:
    stats = {
        'depth_range': depth_range,
        **{f'avg_{param}': group[param].mean() for param in variables_to_plot.keys()}
    }
    rows_list.append(stats)

grouped_overall = data.groupby('overall_range', observed=True)  # Explicitly specify observed=True
for overall_range, group in grouped_overall:
    stats = {
        'depth_range': overall_range,
        **{f'avg_{param}': group[param].mean() for param in variables_to_plot.keys()}
    }
    rows_list.append(stats)

results_df = pd.DataFrame(rows_list)
results_df.to_csv(CSV_SAVE_PATH, index=False)
print(f"Average parameters by depth CSV file has been written to {CSV_SAVE_PATH}")

# Calculate buoyancy frequency squared (N²)
g = 9.81  # Gravity in m/s²
rho0 = data['density'].mean()  # Reference density

# Compute density gradient (dρ/dz)
data['d_density_dz'] = data['density'].diff() / data['depth'].diff()

# Compute buoyancy frequency squared (N²)
data['N2'] = - (g / rho0) * data['d_density_dz']

# Analyze N² values for stratification
data['stratification'] = data['N2'].apply(lambda n2: 'Stable' if n2 > 0 else 'Unstable' if n2 < 0 else 'Neutral')

# Save stratification analysis results
stratification_save_path = os.path.join(CSV_SAVE_DIR, 'stratification_analysis.csv')
data[['depth', 'density', 'N2', 'stratification']].to_csv(stratification_save_path, index=False)
print(f"Stratification analysis results have been written to {stratification_save_path}")

# Plot N² values with depth on y-axis (inverted) and N² on x-axis
N2_plot_save_path = os.path.join(VISUAL_SAVE_DIR, 'N2_plot.png')
plt.figure(figsize=(14, 8))
plt.plot(data['N2'], data['depth'], linestyle='-', marker='o')
plt.title('Buoyancy Frequency Squared (N²) Across Depths', fontsize=20)
plt.xlabel('N² (s⁻²)', fontsize=16)
plt.ylabel('Depth (m)', fontsize=16)
plt.grid(True)
plt.axvline(x=0, color='r', linestyle='--')  # Add a vertical line at N² = 0 for reference
plt.gca().invert_yaxis()  # Invert y-axis to have depth increasing downwards
plt.savefig(N2_plot_save_path, dpi=300, bbox_inches='tight')
plt.show()

print(f"N² analysis plot has been saved to {N2_plot_save_path}")