import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Adjust font sizes for better visibility
plt.rc('axes', titlesize=24)      # Title font size
plt.rc('axes', labelsize=20)      # Axes labels font size
plt.rc('xtick', labelsize=18)     # X-tick labels font size
plt.rc('ytick', labelsize=18)     # Y-tick labels font size
plt.rc('legend', fontsize=18)     # Legend font size

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data')
SATELLITE_DATA_DIR = os.path.join(DATA_DIR, 'sat_default', 'csv_output')
SAVE_DIR = os.path.join(SCRIPT_DIR, '..', 'visualization', 'satellite')
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Define the path to the combined CSV file
combined_csv_file_path = os.path.join(SATELLITE_DATA_DIR, 'combined_chlor_a.csv')

# Read the combined data from the CSV file
combined_data = pd.read_csv(combined_csv_file_path)

# List of sensors in the specified order
sensors = ['modisa', 'hawkeye', 's3a', 's3b']

# Print the number of valid data points for each sensor
for sensor in sensors:
    num_valid_points = combined_data[f'{sensor}_chlor_a'].dropna().size
    print(f'{sensor.capitalize()} has {num_valid_points} valid data points')

# Set up the figure
plt.figure(figsize=(20, 15))

# Define the number of bins
bins = 30

# Create subplots for each sensor
sensor_positions = {
    'modisa': 1,
    'hawkeye': 2,
    's3a': 3,
    's3b': 4
}

for sensor in sensors:
    chlor_a_data = combined_data[f'{sensor}_chlor_a'].dropna()
    
    # Create subplot for each sensor
    plt.subplot(2, 2, sensor_positions[sensor])
    sns.histplot(chlor_a_data, bins=bins, kde=True, color='blue')
    
    plt.title(f'{sensor.capitalize()} Chl a Distribution')
    plt.xlabel('Chl a Concentration (µg/L)')
    plt.ylabel('Counts')
    plt.legend(labels=[f'{sensor.capitalize()} Chl a'])

plt.tight_layout()

# Save the plot
plt.savefig(os.path.join(SAVE_DIR, "chl_distribution.png"), dpi=500, bbox_inches='tight')
plt.close()
