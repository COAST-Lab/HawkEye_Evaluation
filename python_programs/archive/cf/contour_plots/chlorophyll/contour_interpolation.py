# Script Title: Individual Transect Interpolated Chlorophyll Gradient Visualizer
# Author: Mitch Torkelson
# Date: August 2023

# Description: 
# This script reads in transect data from a series of Excel files,
# Calculates the distance along each transect using the haversine formula for lat-long pairs,
# Interpolates and visualizes the Chlorophyll a gradient versus depth for each transect,
# and saves the visualizations as individual PNGs to a specified directory.

# -----------------
# IMPORTS
# -----------------
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from scipy.interpolate import griddata
import cmocean

# -----------------
# CONSTANTS
# -----------------
BASE_DIR = '/Users/macbook/thesis_materials/'
DATA_DIR = os.path.join(BASE_DIR, 'data/acrobat/050323/transects')
SAVE_DIR = os.path.join(BASE_DIR, 'visualization/contour_plots/cf/chlorophyll/contour_interpolation')

# -----------------
# HELPER FUNCTIONS
# -----------------
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    r = 6371
    return c * r

def plot_chlorophyll_gradients(file_names):
    for idx, fname in enumerate(file_names):
        df = pd.read_excel(fname)

        start_lat, start_long = df.iloc[0][['lat', 'long']]
        end_lat, end_long = df.iloc[-1][['lat', 'long']]
        total_distance = haversine(start_long, start_lat, end_long, end_lat)

        df['normalized_distance'] = np.linspace(0, total_distance, len(df))

        xi = np.linspace(df['normalized_distance'].min(), df['normalized_distance'].max(), 500)
        yi = np.linspace(df['depth'].min(), df['depth'].max(), 500)
        xi, yi = np.meshgrid(xi, yi)

        zi = griddata((df['normalized_distance'], df['depth']), df['chlor_a'], (xi, yi), method='linear')
        zi = np.ma.masked_invalid(zi)

        local_min = df['chlor_a'].min()
        local_max = df['chlor_a'].max()
        print(f"Local Chlorophyll Min for transect {idx + 1}: {local_min}")
        print(f"Local Chlorophyll Max for transect {idx + 1}: {local_max}")

        fig, ax = plt.subplots(figsize=(10, 6))

        contour = ax.contourf(xi, yi, zi, 100, cmap=cmocean.cm.algae, vmin=local_min, vmax=local_max)
        cbar = plt.colorbar(contour)
        cbar.set_label('Chlorophyll (µg/L)')

        ax.set_xticks(np.arange(0, total_distance + 0.5, 0.5))
        ax.set_yticks(np.arange(0, df['depth'].max() + 1, 1))
        ax.invert_yaxis()
        ax.set_xlabel('Distance along transect (km)')
        ax.set_ylabel('Depth (m)')
        ax.set_title(f'Chlorophyll gradient of transect {idx + 1}')

        file_save_path = f"{SAVE_DIR}/chlor_a_gradient_transect_{idx + 1}.png"
        try:
            plt.savefig(file_save_path, dpi=300)
            print(f"Plot for transect {idx + 1} generated successfully at {file_save_path}")
        except Exception as e:
            print(f"Error saving plot for transect {idx + 1}: {e}")
        plt.close()
        
# -----------------
# SCRIPT EXECUTION
# -----------------
def main():
    file_names = [os.path.join(DATA_DIR, f'transect_{i}.xlsx') for i in range(1, 3)]
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    plot_chlorophyll_gradients(file_names)

if __name__ == "__main__":
    main()