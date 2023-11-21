# Script Title: Individual Transect Data Gradient Visualizer
# Author: Mitch Torkelson
# Updated: 11/16/2023

# Description: 
# This script processes oceanographic data to visualize the distribution of Chlorophyll a or turbidity along various transects, based on the selected DATA_TYPE. 
# Key functionalities include:
# 1. Reading transect data from a series of Excel files.
# 2. Calculating distances along each transect using the Haversine formula, based on latitude and longitude coordinates.
# 3. Interpolating the selected data type (Chlorophyll a or turbidity), using a specified method ('linear' by default), to create a continuous gradient representation versus depth for each transect.
# 4. Optionally including bathymetry data in the visualizations.
# 5. Saving the visualizations as individual PNG files in a specified directory.

# The script's behavior (including the choice of data type and whether to include bathymetry) is adjustable via the ENABLE_INTERPOLATION, INTERPOLATION_METHOD, ENABLE_BATHYMETRY, and DATA_TYPE constants.

# -----------------
# IMPORTS
# -----------------
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from scipy.interpolate import griddata, interp1d
import cmocean
import rasterio
from geopy.distance import great_circle
from tqdm import tqdm


# -----------------
# CONSTANTS
# -----------------
ENABLE_INTERPOLATION = True   # Set to False to disable chlorophyll data interpolation
INTERPOLATION_METHOD = 'linear'   # options are linear, cubic, or nearest
ENABLE_BATHYMETRY = True       # Set to True to include bathymetry data, False to exclude it
DATA_TYPE = 'turbidity'          # Set to 'chlor_a' for Chlorophyll a data or 'turbidity' for turbidity data
TURBIDITY_CONTOUR_LEVEL = 5.0  # Threshold for turbidity concentration to overlay contour lines
CHLOROPHYLL_CONTOUR_LEVEL = 1.0  # Threshold for Chlorophyll a concentration to overlay contour lines

BASE_DIR = '/Users/macbook/thesis_materials'
DATA_DIR = os.path.join(BASE_DIR, 'data/acrobat/050523/transects/processed_transects')

# Dynamically set the SAVE_DIR based on the DATA_TYPE and INTERPOLATION_METHOD
SAVE_DIR = os.path.join(BASE_DIR, f'visualization/contour_plots/wb/{DATA_TYPE}/2D_plots/contour_interp/{INTERPOLATION_METHOD}')
if not ENABLE_INTERPOLATION:
    SAVE_DIR = os.path.join(BASE_DIR, f'visualization/contour_plots/wb/{DATA_TYPE}/2D_plots/contours')

BATHYMETRY_PATH = os.path.join(BASE_DIR, 'python/helper_data/bathymetry/gebco_2023_n34.5_s33.75_w-78.0_e-77.3.tif')
NUM_CONTOUR_LEVELS = 100  # Number of contour levels in the plot
EARTH_RADIUS = 6371  # in kilometers
SHOW_TRANSECT_TITLE = False   # Set to False to hide transect titles
SHOW_AXES_TITLES = False       # Set to False to hide axes titles
SHOW_COLORBAR = True          # Set to False to hide the colorbar

# -----------------
# HELPER FUNCTIONS
# -----------------
def haversine(lon1, lat1, lon2, lat2):
    # Calculate the great circle distance between two points on the earth (specified in decimal degrees)
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return c * EARTH_RADIUS

def get_global_min_max(file_names):
    # Function to get the global min and max values from all the files for the specified data type.
    all_mins = []
    all_maxs = []

    for fname in tqdm(file_names):
        try:
            data = pd.read_excel(fname)
            all_mins.append(data[DATA_TYPE].min())
            all_maxs.append(data[DATA_TYPE].max())
        except Exception as e:
            print(f"Error processing file {fname}: {e}")

    return min(all_mins), max(all_maxs)

def load_bathymetry(file_path):
    # Load bathymetry data from a GeoTIFF file
    with rasterio.open(file_path) as src:
        bathymetry_data = src.read(1)
        transform = src.transform
    return bathymetry_data, transform

def plot_transect_gradients(file_names, bathymetry_data, transform, global_min, global_max, include_bathymetry):
    # Plot the gradients for each transect based on DATA_TYPE
    max_distance = 0
    print(f"Generating {DATA_TYPE} gradient plots...")
    for idx, fname in enumerate(tqdm(file_names)):
        df = pd.read_excel(fname)
        accumulated_distance = [0]

        # Calculate accumulated distances along the transect
        for i in range(1, len(df)):
            if i % 10 == 0:
                lon1, lat1 = df.iloc[i - 10][['long', 'lat']]
                lon2, lat2 = df.iloc[i][['long', 'lat']]
                distance = haversine(lon1, lat1, lon2, lat2)
                accumulated_distance.append(accumulated_distance[-1] + distance)
            else:
                accumulated_distance.append(accumulated_distance[-1])

        max_distance = max(max_distance, accumulated_distance[-1])
        df['normalized_distance'] = accumulated_distance

        # Define colormap and other variables outside the conditional branches
        if DATA_TYPE == 'chlor_a':
            colormap = cmocean.cm.algae
            overlay_level = CHLOROPHYLL_CONTOUR_LEVEL
            data_label = 'Chlorophyll (µg/L)'
        elif DATA_TYPE == 'turbidity':
            colormap = cmocean.cm.turbid
            overlay_level = TURBIDITY_CONTOUR_LEVEL
            data_label = 'Turbidity (NTU)'

        # Initialize max_depth based on the depth data
        max_depth = df['depth'].max()

        # Interpolation setup
        num_x_points = round(len(df) / 10)
        num_y_points = round(df['depth'].nunique() / 5)

        xi = np.linspace(df['normalized_distance'].min(), df['normalized_distance'].max(), num_x_points)
        yi = np.linspace(df['depth'].min(), df['depth'].max(), num_y_points)
        xi, yi = np.meshgrid(xi, yi)

        fig, ax = plt.subplots(figsize=(10, 10))

        if ENABLE_INTERPOLATION:
            # Interpolation of the data
            zi = griddata((df['normalized_distance'], df['depth']), df[DATA_TYPE], (xi, yi), method=INTERPOLATION_METHOD)
            zi = np.ma.masked_invalid(zi)
            contour = ax.contourf(xi, yi, zi, NUM_CONTOUR_LEVELS, cmap=colormap, vmin=global_min, vmax=global_max)

            if SHOW_COLORBAR:
                cbar = plt.colorbar(contour, ticks=np.linspace(0, 10, 11))
                cbar.set_label(data_label)

            # Overlay contour lines based on the threshold level
            CS = ax.contour(xi, yi, zi, levels=[overlay_level], colors='red', linewidths=1)
        else:
            # Plot using scatter for non-interpolated data
            scatter = ax.scatter(df['normalized_distance'], df['depth'], c=df[DATA_TYPE], cmap=colormap, s=5)
            if SHOW_COLORBAR:
                plt.colorbar(scatter, label=data_label)

        # Overlay a line representing the original data points
        ax.plot(df['normalized_distance'], df['depth'], color='black', linewidth=1, linestyle='dotted')

        if include_bathymetry:
            # Get start and end points of the transect
            start_long, start_lat = df.iloc[0][['long', 'lat']]
            end_long, end_lat = df.iloc[-1][['long', 'lat']]

            # Convert the lat-long to row-col in the GeoTIFF
            col_start, row_start = map(int, ~transform * (start_long, start_lat))
            col_end, row_end = map(int, ~transform * (end_long, end_lat))

            # Slice the bathymetry data and interpolate it
            sliced_bathymetry_data = bathymetry_data[min(row_start, row_end):max(row_start, row_end),
                                                     min(col_start, col_end):max(col_start, col_end)].mean(axis=0)

            # Reverse the sliced bathymetry data for the new orientation
            sliced_bathymetry_data = sliced_bathymetry_data[::-1]

            f = interp1d(np.linspace(0, max_distance, len(sliced_bathymetry_data)),
                         sliced_bathymetry_data, kind='cubic')
            bathy_at_transect = f(df['normalized_distance'])

            # Ensure bathymetric depths are positive
            bathy_at_transect = np.abs(bathy_at_transect)

            # Update max_depth if necessary
            max_depth = max(max_depth, np.max(bathy_at_transect)) + 1  # Add 1 for margin

            # Plotting the bathymetric data along the bottom
            ax.plot(df['normalized_distance'], bathy_at_transect, 'k-', linewidth=2)

            # Fill the area below the bathymetric line (higher depth values)
            ax.fill_between(df['normalized_distance'], max_depth, bathy_at_transect, color='gray', alpha=0.5)

        # Adjust layout to minimize white space
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

        # Set plot limits and labels
        min_depth = 0
        ax.set_ylim([min_depth, max_depth])  # Use the calculated max_depth
        ax.invert_yaxis()

        if SHOW_AXES_TITLES:
            ax.set_xlabel('Distance along transect (km)')
            ax.set_ylabel('Depth (m)')

        if SHOW_TRANSECT_TITLE:
            ax.set_title(f'{DATA_TYPE.capitalize()} gradient of transect {idx + 1}')

        plt.savefig(f"{SAVE_DIR}/transect_{idx + 1}.png", dpi=300, bbox_inches='tight')
        plt.close()
# -----------------
# SCRIPT EXECUTION
# -----------------
def main():
    file_names = [os.path.join(DATA_DIR, f'transect_{i}.xlsx') for i in range(1, 8)]
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    bathymetry_data, transform = load_bathymetry(BATHYMETRY_PATH) if ENABLE_BATHYMETRY else (None, None)
    print("Loading bathymetry data..." if ENABLE_BATHYMETRY else "Skipping bathymetry data...")

    global_min, global_max = get_global_min_max(file_names)
    print(f"{DATA_TYPE.capitalize()} Global min: {global_min}, Global max: {global_max}")

    plot_transect_gradients(file_names, bathymetry_data, transform, global_min, global_max, ENABLE_BATHYMETRY)

    print("Visualization complete. Check the output directory for plots.")

if __name__ == "__main__":
    main()
