# Script Title: Combined Interpolated Transect Chlorophyll Gradient Visualizer
# Author: Mitch Torkelson
# Date: August 2023

# Description: 
# This script reads in transect data from a series of Excel files,
# Calculates the distance along each transect using the haversine formula for lat-long pairs,
# Interpolates and visualizes the Chlorophyll a gradient versus depth for each transect in a 
# single figure, which is saved as individual PNGs to a specified directory.

# -----------------
# IMPORTS
# -----------------
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import pandas as pd
import os
from scipy.interpolate import griddata
import cmocean

# -----------------
# CONSTANTS
# -----------------
BASE_DIR = '/Users/macbook/thesis_materials'
DATA_DIR = os.path.join(BASE_DIR, 'data/acrobat/050523/transects/processed_transects')
SAVE_DIR = os.path.join(BASE_DIR, 'visualization/contour_plots/wb/chlorophyll/mosaics')

# -----------------
# HELPER FUNCTIONS
# -----------------
# Haversine Function
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    r = 6371
    return c * r

def get_global_chlorophyll_limits(file_names):
    # Compute the global minimum and maximum chlorophyll values across all files.
    all_chlor_a_values = []
    
    for fname in file_names:
        df = pd.read_excel(fname)
        all_chlor_a_values.extend(df['chlor_a'].values)
    
    return min(all_chlor_a_values), max(all_chlor_a_values)

def plot_transect_data(df, ax, global_min_chlor_a, global_max_chlor_a):
    # Initialize a list to store accumulated distance
    accumulated_distance = [0]

    # Calculate the accumulated distance along the transect
    for i in range(1, len(df)):
        lat1, long1 = df.iloc[i-1][['lat', 'long']]
        lat2, long2 = df.iloc[i][['lat', 'long']]
        
        # Only add distance if current point is forward (or same position) in transect
        if lat2 >= lat1 and long2 >= long1:
            distance = haversine(long1, lat1, long2, lat2)
            accumulated_distance.append(accumulated_distance[-1] + distance)
        else:
            accumulated_distance.append(accumulated_distance[-1])  # Use the same accumulated value for backtracking points

    df['normalized_distance'] = accumulated_distance
    total_distance = accumulated_distance[-1]

    # Create a grid for interpolation
    xi = np.linspace(df['normalized_distance'].min(), df['normalized_distance'].max(), 500)
    yi = np.linspace(df['depth'].min(), df['depth'].max(), 500)
    xi, yi = np.meshgrid(xi, yi)

    # Interpolate the data
    zi = griddata((df['normalized_distance'], df['depth']), df['chlor_a'], (xi, yi), method='linear')
    zi = np.ma.masked_invalid(zi)

    # Use global min and max for contour plot
    contour = ax.contourf(xi, yi, zi, 100, cmap=cmocean.cm.algae, vmin=global_min_chlor_a, vmax=global_max_chlor_a)

    # Setting the axis labels and title
    ax.set_xticks(np.arange(0, total_distance + 0.5, 0.5))
    ax.set_ylim(0, 11)
    ax.invert_yaxis()
    ax.set_xlabel('Distance along transect (km)')
    ax.set_ylabel('Depth (m)')

    return contour

def main():
    # Load data files
    print("Loading transect data files...")
    file_names = [os.path.join(DATA_DIR, f'cleaned_data_transect_{i}.xlsx') for i in range(1, 8)]

    # Extract global chlorophyll limits
    global_min_chlor_a, global_max_chlor_a = get_global_chlorophyll_limits(file_names)

    # Print the global min and max chlorophyll values to the terminal
    print(f"Global Minimum Chlorophyll: {global_min_chlor_a} µg/L")
    print(f"Global Maximum Chlorophyll: {global_max_chlor_a} µg/L")

    # Create directory for saving if it doesn't exist
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # Create the subplots
    fig = plt.figure(figsize=(28, 12))  # Create an empty figure
    fig.suptitle('Interpolated Transect Chlorophyll Gradient', fontsize=24)

    plt.subplots_adjust(left=0.05, right=0.9, top=0.9, bottom=0.05, wspace=0.2, hspace=0.2)

    # Manually create 7 subplots (2 rows x 4 columns, skipping the last one)
    nrows, ncols = 2, 4
    for idx in range(7):
        print(f"Visualizing data for Transect {idx + 1}...")
        row, col = divmod(idx, ncols)
        ax = fig.add_subplot(nrows, ncols, idx + 1)
        
        fname = os.path.join(DATA_DIR, f'transect_{idx + 1}.xlsx')
        
        # Add titles to subplots
        ax.set_title(f'Transect {idx + 1}')

        df = pd.read_excel(fname)
        contour = plot_transect_data(df, ax, global_min_chlor_a, global_max_chlor_a)
        
    # Create an axes to hold the colorbar
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])

    # Create an independent colorbar using global min and max
    norm = Normalize(vmin=global_min_chlor_a, vmax=global_max_chlor_a)
    sm = plt.cm.ScalarMappable(cmap=cmocean.cm.algae, norm=norm)
    sm.set_array([])  # Dummy array, data is not actually needed for colorbar
    cbar_ticks = np.linspace(global_min_chlor_a, global_max_chlor_a, 11)
    cbar = fig.colorbar(sm, cax=cbar_ax, ticks=cbar_ticks, orientation='vertical')
    cbar.set_label('Chlorophyll (µg/L)')    

    # Save and show the plot
    print(f"Saving the combined chlorophyll gradients visualization to {SAVE_DIR}...")
    plt.savefig(f"{SAVE_DIR}/all_interpolated_transects.png", dpi=300)
    print(f"Visualization saved successfully as combined_chlor_a_gradients.png!")
    
# -----------------
# SCRIPT EXECUTION
# -----------------
if __name__ == "__main__":
    main()