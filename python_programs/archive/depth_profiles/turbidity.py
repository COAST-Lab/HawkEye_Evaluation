# Script Title: Turbidity Depth Profiles Visualization (All transects)
# Author: Mitch Torkelson
# Date: August 2023

# Description:
# This script visualizes the depth profiles for turbidity data from all "cleaned"
# transect data files. For each transect, two plots are produced side by side:
# 1. Depth vs Turbidity
# 2. Distribution of Turbidity at different depth bins.
# The generated plots are saved as image files.

# -----------------
# IMPORTS
# -----------------
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# -----------------
# CONSTANTS
# -----------------
BASE_DIR = '/Users/macbook/thesis_materials'
DATA_DIR = os.path.join(BASE_DIR, 'data/acrobat/050523/transects/cleaned_data')
SAVE_DIR = os.path.join(BASE_DIR, 'visualization/depth_profiles/turbidity')
FILE_NAMES = [os.path.join(DATA_DIR, f'cleaned_data_transect_{i}.xlsx') for i in range(1, 8)]

# -----------------
# HELPER FUNCTIONS
# -----------------
def load_all_data():
    data = [pd.read_excel(file) for file in FILE_NAMES]
    min_turbidity = np.min([df['turbidity'].min() for df in data])
    max_turbidity = np.max([df['turbidity'].max() for df in data])
    min_depth = np.min([df['depth'].min() for df in data])
    max_depth = np.max([df['depth'].max() for df in data])
    return data, min_turbidity, max_turbidity, min_depth, max_depth

def plot_depth_profiles(df, i, min_turbidity, max_turbidity, min_depth, max_depth):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 8), gridspec_kw={'width_ratios': [3, 1]}, sharey=True)
    
    # Plotting Depth vs Turbidity
    ax1.plot(df['turbidity'], df['depth'])
    ax1.set_title(f'Transect {i}')
    ax1.set_xlabel('Turbidity (NTU)')
    ax1.set_ylabel('Depth (m)')
    ax1.set_xlim(min_turbidity, max_turbidity)
    ax1.set_ylim(10, 0)
    ax1.invert_yaxis()
    ax1.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
    
    # Boxplot of Turbidity Distribution at Different Depth Bins
    depth_bins = np.arange(0, 10 + 2, 2)
    bin_centers = (depth_bins[:-1] + depth_bins[1:]) / 2
    grouped = df.groupby(pd.cut(df['depth'], depth_bins))
    turbidity_values = [group['turbidity'].dropna().values for _, group in grouped]
    ax2.boxplot(turbidity_values, vert=False, positions=bin_centers)
    ax2.set_xlabel('Turbidity Distribution')
    ax2.invert_yaxis()
    ax2.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)

    # Custom y-ticks
    y_ticks = np.arange(0, 10.5, 0.5)
    y_tick_labels = [str(int(y)) if y.is_integer() else "" for y in y_ticks]
    ax1.set_yticks(y_ticks)
    ax1.set_yticklabels(y_tick_labels)
    ax2.set_yticks(y_ticks)
    ax2.set_yticklabels(y_tick_labels)

    plt.savefig(os.path.join(SAVE_DIR, f'depth_profile_turbidity_transect_{i}.png'))
    plt.close()

# -----------------
# SCRIPT EXECUTION
# -----------------
def main():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    all_data, global_min_turbidity, global_max_turbidity, global_min_depth, global_max_depth = load_all_data()

    for i, df in enumerate(all_data, start=1):
        plot_depth_profiles(df, i, global_min_turbidity, global_max_turbidity, global_min_depth, global_max_depth)
        print(f"Depth profile plotted for transect {i} and saved to {SAVE_DIR}.")

if __name__ == '__main__':
    main()
