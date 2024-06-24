import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# Define directories and paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'acrobat', 'transects', 'processed')
ACROBAT_DIR = os.path.join(DATA_DIR, 'processed_dataset.csv')

# Load the dataset
print("Loading data...")
data = pd.read_csv(ACROBAT_DIR)
print("Data loaded successfully.")

# Define parameters to plot and their units
variables_to_plot = {
    'temp': 'Temperature (°C)',
    'salinity': 'Salinity (psu)',
    'turbidity': 'Turbidity (NTU)',
    'chlor_a': 'Chlorophyll-a (µg/L)',
    'do': 'Dissolved Oxygen (mg/L)',
    'density': 'Density (kg/m³)'
}

# Calculate mean parameter measurement for transects 1-7
transect_1_7_mean = data[data['transect_id'].isin(range(1, 8))].groupby('transect_id')[list(variables_to_plot.keys())].mean()

# Function to create line graph for each variable
def create_line_graph(data, variable, unit):
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data[variable], marker='o', linestyle='-', color='b')
    plt.title(f'Mean {variable.capitalize()} from Transect 1 to Transect 7')
    plt.xlabel('Transect ID')
    plt.ylabel(unit)
    plt.grid(True)

    # Remove scientific notation
    ax = plt.gca()
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False, useMathText=False))
    plt.xticks(data.index)
    plt.savefig(os.path.join(SCRIPT_DIR, f'{variable}_mean_transect_1_to_7.png'), dpi=300, bbox_inches='tight')
    plt.close()

# Generate line graph for each variable
for variable, unit in variables_to_plot.items():
    create_line_graph(transect_1_7_mean, variable, unit)
    print(f"Line graph for {variable} created.")

print("All line graphs created successfully.")
