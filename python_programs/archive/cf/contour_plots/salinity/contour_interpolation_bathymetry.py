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
import rasterio
from geopy.distance import great_circle
from scipy.interpolate import interp1d



# -----------------
# CONSTANTS
# -----------------
BASE_DIR = '/Users/macbook/thesis_materials'
DATA_DIR = os.path.join(BASE_DIR, 'data/acrobat/050323/transects')
SAVE_DIR = os.path.join(BASE_DIR, 'visualization/contour_plots/cf/salinity/contour_interpolation_bathymetry')

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

# Function to get the global min and max values from all the files for salinity.
def get_global_min_max(file_names):
    all_mins = []
    all_maxs = []
    for fname in file_names:
        try:
            data = pd.read_excel(fname)
            local_min = data['salinity'].min()
            local_max = data['salinity'].max()
            all_mins.append(local_min)
            all_maxs.append(local_max)
        except Exception as e:
            print(f"Error processing file {fname}: {e}")
    return min(all_mins), max(all_maxs)

def load_bathymetry(file_path):
    with rasterio.open(file_path) as src:
        bathymetry_data = src.read(1)
        transform = src.transform
    return bathymetry_data, transform

def plot_salinity_gradients(file_names, bathymetry_data, transform, global_min, global_max):
    for idx, fname in enumerate(file_names):
        df = pd.read_excel(fname)

        # Calculate local min and max salinity values for this transect
        local_min = df['salinity'].min()
        local_max = df['salinity'].max()
        print(f"Local salinity min for transect {idx + 1}: {local_min}")
        print(f"Local salinity max for transect {idx + 1}: {local_max}")

        start_lat, start_long = df.iloc[0][['lat', 'long']]
        end_lat, end_long = df.iloc[-1][['lat', 'long']]
        total_distance = haversine(start_long, start_lat, end_long, end_lat)

        df['normalized_distance'] = np.linspace(0, total_distance, len(df))

        xi = np.linspace(df['normalized_distance'].min(), df['normalized_distance'].max(), 500)
        yi = np.linspace(df['depth'].min(), df['depth'].max(), 500)
        xi, yi = np.meshgrid(xi, yi)

        zi = griddata((df['normalized_distance'], df['depth']), df['salinity'], (xi, yi), method='linear')
        zi = np.ma.masked_invalid(zi)

        fig, ax = plt.subplots(figsize=(10, 6))

        # Convert the lat-long to row-col in the GeoTIFF
        col_start, row_start = map(int, ~transform * (start_long, start_lat))
        col_end, row_end = map(int, ~transform * (end_long, end_lat))

        # Slice the bathymetry data and interpolate it
        sliced_bathymetry_data = bathymetry_data[min(row_start, row_end):max(row_start, row_end),
                                                 min(col_start, col_end):max(col_start, col_end)].mean(axis=0)
        f = interp1d(np.linspace(0, total_distance, len(sliced_bathymetry_data)), 
                     sliced_bathymetry_data, kind='linear')
        bathy_at_transect = f(xi[0, :])
        
        # Ensure bathymetric depths are positive
        bathy_at_transect = np.abs(bathy_at_transect)

        # Determine the maximum depth needed for y-axis scaling
        max_depth = max(df['depth'].max(), np.max(bathy_at_transect))
        min_depth = min(0, np.min(bathy_at_transect))  # Usually zero, but just in case

        print(f"Calculated max_depth of transect {idx + 1}: {max_depth}")

        # Fill the area below the bathymetric line (higher depth values)
        ax.fill_between(xi[0, :], max_depth + 1, bathy_at_transect, color='gray', alpha=0.5)

        # Fill the area above the bathymetric line (lower depth values) with a light shade of blue
        ax.fill_between(xi[0, :], min_depth, bathy_at_transect, color='lightblue', alpha=0.5)

        contour = ax.contourf(xi, yi, zi, 100, cmap=cmocean.cm.haline, vmin=global_min, vmax=global_max)
        cbar = plt.colorbar(contour)
        cbar.set_label('Salinity (psu)')

        # Plotting the bathymetric data along the bottom
        ax.plot(xi[0, :], bathy_at_transect, 'k-', linewidth=2)

        # Set the y-limits and invert the axis
        ax.set_ylim([min_depth, max_depth + 1])  # Extend the lower limit by 1 meter (or more if needed)
        ax.invert_yaxis()

        # Set the y-ticks dynamically
        tick_interval = 1  # Set the tick interval as per your requirement
        ax.set_yticks(np.arange(0, max_depth + 1, tick_interval))
        
        ax.set_xlabel('Distance along transect (km)')
        ax.set_ylabel('Depth (m)')
        ax.set_title(f'Salinity gradient of transect {idx + 1}')
        
        plt.savefig(f"{SAVE_DIR}/salinity_gradient_transect_{idx + 1}.png", dpi=300)
        plt.close()

# -----------------
# SCRIPT EXECUTION
# -----------------
def main():
    file_names = [os.path.join(DATA_DIR, f'transect_{i}.xlsx') for i in range(1, 3)]
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # Calculate the global min and max salinity values
    global_min, global_max = get_global_min_max(file_names)
    print(f"Salinity Global min: {global_min}, Global max: {global_max}")

    # Load bathymetry data
    bathymetry_path = '/Users/macbook/thesis_materials/python/bathymetry/gebco_2023_n34.5_s33.75_w-78.0_e-77.3.tif'
    bathymetry_data, transform = load_bathymetry(bathymetry_path)

    # Generate the plots
    plot_salinity_gradients(file_names, bathymetry_data, transform, global_min, global_max)


if __name__ == "__main__":
    main()