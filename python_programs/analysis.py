import pandas as pd
from scipy.stats import kruskal
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch
import numpy as np
import os

# Define directories and paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'acrobat', 'transects', 'processed')
ACROBAT_FILE_PATH = os.path.join(DATA_DIR, 'processed_dataset.csv')
VISUAL_SAVE_DIR = os.path.join(SCRIPT_DIR, '..', 'visualization', 'transect_analysis')

# Load your dataset
data = pd.read_csv(ACROBAT_FILE_PATH)

# Print the columns in the dataset
print("Columns in the dataset:")
print(data.columns)

# Get the unique transect_ids
unique_transects = data['transect_id'].unique()
print("Available transects for analysis:")
print(unique_transects)

# Define depth bins and labels
depth_bins = [0, 2, 4, 6, 8, 10]
depth_labels = ['0-2', '2-4', '4-6', '6-8', '8-10']

# Bin the depth data
data['depth_range'] = pd.cut(data['depth'], bins=depth_bins, labels=depth_labels, right=False)

# List of oceanic parameters to analyze
parameters = ['temp', 'salinity', 'chlor_a', 'turbidity', 'do', 'density']

for param in parameters:
    print(f"\nAnalyzing parameter: {param}\n")
    results = {}
    for depth_range in depth_labels:
        depth_data = data[data['depth_range'] == depth_range]
        transect_params = [depth_data[depth_data['transect_id'] == transect][param].dropna() for transect in unique_transects]

        # Print the number of observations in each group
        group_sizes = [len(tp) for tp in transect_params]
        print(f"Depth range: {depth_range} group sizes: {group_sizes}")

        # Perform Kruskal-Wallis H-test for independent samples
        if all(len(tp) > 0 for tp in transect_params):
            h_stat, p_value = kruskal(*transect_params)
        else:
            h_stat, p_value = float('nan'), float('nan')
        
        results[depth_range] = {'H-statistic': h_stat, 'P-value': p_value}

        # Print results for each depth range
        print(f"Depth range: {depth_range}")
        print(f"H-statistic: {h_stat}")
        print(f"P-value: {p_value}")
        significance = "statistically significant" if p_value < 0.05 else "not statistically significant"
        print(f"The difference in mean {param} across transects for depth range {depth_range} is {significance}.\n")

        # Calculate and print effect size (eta-squared)
        if not np.isnan(h_stat):
            eta_squared = h_stat / (len(data) - 1)
            print(f"Effect size (eta-squared) for depth range {depth_range}: {eta_squared}")

    # Plot the parameter distributions for each transect using seaborn with the viridis color palette
    plt.figure(figsize=(15, 10))
    boxplot = sns.boxplot(x='transect_id', y=param, hue='depth_range', data=data, palette='viridis')
    plt.title(f'{param.capitalize()} Distribution Across Transects and Depth Ranges')
    plt.xlabel('Transect ID')
    plt.ylabel(f'{param.capitalize()}')

    # Create custom legend handles with p-values
    handles, labels = boxplot.get_legend_handles_labels()
    custom_labels = [f"{label} (p-value: {results[label]['P-value']:.4f})" for label in labels]
    colors = sns.color_palette('viridis', len(depth_labels))
    custom_handles = [Patch(facecolor=color, label=custom_label) for color, custom_label in zip(colors, custom_labels)]

    # Place the custom legend inside the plot
    plt.legend(handles=custom_handles, title='Depth Range (m)', bbox_to_anchor=(1, 1), loc='upper left')

    # Save the figure
    output_path = os.path.join(VISUAL_SAVE_DIR, f'{param}_transect_depth_ranges.png')
    plt.savefig(output_path, bbox_inches='tight')
