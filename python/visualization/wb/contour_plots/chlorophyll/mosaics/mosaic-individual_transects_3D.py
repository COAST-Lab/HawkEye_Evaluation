# -----------------
# IMPORTS
# -----------------
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import os
import cmocean
from scipy.interpolate import griddata

# -----------------
# CONSTANTS
# -----------------
BASE_DIR = '/Users/macbook/thesis_materials'
DATA_DIR = os.path.join(BASE_DIR, 'data/acrobat/050523/transects/processed_transects')
SAVE_DIR = '/Users/macbook/thesis_materials/visualization/contour_plots/wb/chlorophyll/mosaics'
MAP_IMAGE_PATH = '/Users/macbook/thesis_materials/visualization/maps/transects_wb.png'
PROVIDED_IMAGE_PATH = '/Users/macbook/thesis_materials/visualization/contour_plots/wb/chlorophyll/contour_interpolation_3D_accumulated/3D_chlorophyll_plot_upto_transect_6.png'
SHORE_POINT = (-77.802938, 34.195220)


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

def get_global_min_max_chlor_a(file_names):
    global_min = float('inf')
    global_max = -float('inf')

    for fname in file_names:
        df = pd.read_excel(fname)
        local_min = df['chlor_a'].min()
        local_max = df['chlor_a'].max()

        print(f"File {fname} has local min: {local_min} µg/L and local max: {local_max} µg/L")
        
        global_min = min(global_min, local_min)
        global_max = max(global_max, local_max)

    return global_min, global_max

def plot_combined_transects_3d_chlorophyll_gradient_with_map(file_names, global_min, global_max):
    distances_from_shore = []
    dfs = []  # Store DataFrames after reading them

    for fname in file_names:
        df = pd.read_excel(fname)
        dfs.append(df)
        middle_idx = len(df) // 2
        middle_lat, middle_long = df.iloc[middle_idx][['lat', 'long']]
        distance_from_shore = haversine(SHORE_POINT[0], SHORE_POINT[1], middle_long, middle_lat)
        distances_from_shore.append(distance_from_shore)

    sorted_files_and_dfs = sorted(zip(distances_from_shore, dfs, file_names))

    # Create a figure for combined plots (3x3 grid)
    fig = plt.figure(figsize=(30, 20))

    # Load and display the study map image
    map_img = plt.imread(MAP_IMAGE_PATH)
    ax_map = fig.add_subplot(3, 3, 1)
    ax_map.imshow(map_img)
    ax_map.axis('off')  # Turn off axis for the map
    ax_map.set_title("Study Area Map")  # Title for the map

    # Loop through each transect
    for idx, (distance, df, fname) in enumerate(sorted_files_and_dfs):
        subplot_idx = idx + 2  # Since the first plot is the map
        print(f"Interpolating and visualizing data for file: {fname}...")
        print(f"Distance from Shore for Transect {subplot_idx - 1}: {distance} km")

        ax = fig.add_subplot(3, 3, subplot_idx, projection='3d')

        accumulated_distance = [0]
        
        # Calculate the accumulated distance for this file
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

        distance_from_shore = distances_from_shore[idx]  # Using the pre-calculated distance from shore

        # Print the calculated distance
        print(f"Distance from Shore for Transect {idx+1}: {distance_from_shore} km")

        # Interpolation
        yi = np.linspace(df['normalized_distance'].min(), df['normalized_distance'].max(), 100)
        zi = np.linspace(df['depth'].min(), df['depth'].max(), 100)
        yi, zi = np.meshgrid(yi, zi)

        xi = np.full(yi.shape, distance_from_shore)  # Distance from shore replaces the transect index

        colors = griddata((df['normalized_distance'], df['depth']), df['chlor_a'], (yi, zi), method='linear')

        # Plotting
        ax.scatter(xi, yi, zi, c=colors.flatten(), cmap=cmocean.cm.algae, marker='o', alpha=0.6, vmin=global_min, vmax=global_max)

        ax.set_xlabel('Distance from Shore (km)')
        ax.set_ylabel('Distance along transect (km)')
        ax.set_zlabel('Depth (m)')

        ax.set_xlim(2.5, 4.5)
        tick_spacing = (4.5 - 2.5) / 10
        ax.set_xticks(np.arange(2.5, 4.5 + tick_spacing, tick_spacing))
        
        ax.set_ylim(ax.get_ylim()[::-1])
        ax.set_zlim(ax.get_zlim()[::-1])

        ax.set_title(f"Transect {idx + 1}")  # Add title to each subplot

    # Load and display the provided image in the bottom right of the 3x3 grid
    provided_img = plt.imread(PROVIDED_IMAGE_PATH)
    ax_provided_img = fig.add_subplot(3, 3, 9)
    ax_provided_img.imshow(provided_img)
    ax_provided_img.axis('off')  # Turn off axis for the provided image
    ax_provided_img.set_title("Additional Visualization")  # Title for the provided image

    # Adjust layout and add colorbar
    plt.tight_layout(pad=1.0)  # Reduced padding
    sm = plt.cm.ScalarMappable(cmap=cmocean.cm.algae, norm=plt.Normalize(vmin=global_min, vmax=global_max))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=fig.axes, ticks=np.linspace(global_min, global_max, 11)) 
    cbar.set_label('Chlorophyll (µg/L)')

    # Save the combined visualization
    combined_save_path = f"{SAVE_DIR}/combined_3D_chlorophyll_plot_with_map.png"
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    plt.savefig(combined_save_path, dpi=300, bbox_inches='tight')  # Tight bounding box
    plt.close()  # Close the figure to free up memory

# -----------------
# MAIN FUNCTION
# -----------------
def main():
    if not os.path.exists(DATA_DIR):
        print(f"Data directory does not exist: {DATA_DIR}")
        return

    file_names = [os.path.join(DATA_DIR, f'transect_{i}.xlsx') for i in range(1, 8)]
    global_min, global_max = get_global_min_max_chlor_a(file_names)

    print("Creating combined 3D visualizations of Chlorophyll gradients with study map...")
    plot_combined_transects_3d_chlorophyll_gradient_with_map(file_names, global_min, global_max)
    print("Combined visualization with study map complete. Check the output directory for the PNG file.")

if __name__ == "__main__":
    main()
