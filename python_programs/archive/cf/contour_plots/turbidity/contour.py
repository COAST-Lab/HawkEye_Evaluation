# Script Title: Individual Transect Turbidity Gradient Scatter Plot Visualizer
# Author: Mitch Torkelson
# Date: August 2023

# Description: 
# This script reads in transect data from a series of Excel files, 
# Calculates the distance along the transect using the haversine formula for lat-long pairs,
# Visualizes the Turbidity gradient versus depth for each transect using scatter plots,
# Saves each scatter plot visualization as individual PNGs to a specified directory.


# -----------------
# IMPORTS
# -----------------
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import cmocean


# -----------------
# CONSTANTS
# -----------------
BASE_DIR = '/Users/macbook/thesis_materials/'
DATA_DIR = os.path.join(BASE_DIR, 'data/acrobat/050323/transects')
SAVE_DIR = os.path.join(BASE_DIR, 'visualization/contour_plots/cf/turbidity/contour')


# -----------------
# HELPER FUNCTIONS
# -----------------
# Compute distance between two points on Earth using the Haversine formula
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    r = 6371  # Radius of Earth in kilometers
    return c * r

# Loop through each Excel file, read the data, and plot the chlorophyll gradients.
def plot_turbidity_gradients(file_names):
    plt.style.use('ggplot')
    
    for idx, file in enumerate(file_names):
        if not os.path.exists(file):
            print(f"File not found: {file}")
            continue
        try:
            df = pd.read_excel(file)
        except Exception as e:
            print(f"Error reading file {file}: {e}")
            continue
        
        start_lat, start_long = df.iloc[0][['lat', 'long']]
        end_lat, end_long = df.iloc[-1][['lat', 'long']]
        total_distance = haversine(start_long, start_lat, end_long, end_lat)
        
        df['normalized_distance'] = np.linspace(0, total_distance, len(df))

        turbidity_min = df['turbidity'].min()
        turbidity_max = df['turbidity'].max()

        # Print the min and max turbidity values to the terminal
        print(f"Transect {idx + 1}: Turbidity min value: {turbidity_min:.2f}, max value: {turbidity_max:.2f}")

        plt.figure(figsize=(10, 6))
        plt.scatter(df['normalized_distance'], df['depth'], c=df['turbidity'], cmap=cmocean.cm.turbid, s=5, vmin=turbidity_min, vmax=turbidity_max)
        
        # Setting custom x and y ticks
        plt.xticks(np.arange(0, total_distance + 0.5, 0.5))
        plt.yticks(np.arange(0, df['depth'].max() + 1, 1))
        
        cbar = plt.colorbar(label='Turbidity (NTU)')
        cbar_ticks = np.linspace(turbidity_min, turbidity_max, num=5)
        cbar.set_ticks(cbar_ticks)
        
        plt.gca().invert_yaxis()
        plt.xlabel('Distance along transect (km)')
        plt.ylabel('Depth (m)')
        plt.title(f'Turbidity gradient of transect {idx + 1}')
        plt.savefig(f"{SAVE_DIR}/turbidity_gradient_{idx + 1}.png")
        plt.close()

    # Print completion message to the terminal
    print("All plots have been successfully generated!")

# -----------------
# SCRIPT EXECUTION
# -----------------
def main():
    file_names = [os.path.join(DATA_DIR, f'transect_{i}.xlsx') for i in range(1, 3)]
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    plot_turbidity_gradients(file_names)

if __name__ == "__main__":
    main()