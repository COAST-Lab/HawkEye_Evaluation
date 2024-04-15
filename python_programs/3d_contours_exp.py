
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import os
import cmocean
from scipy.interpolate import griddata
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from tqdm import tqdm
from PIL import Image


INTERPOLATION_METHOD = 'linear' # linear, cubic, nearest
DATA_TYPE = 'chlor_a'  # options are 'temp', 'salinity', 'density', 'turbidity', 'cdom', 'chlor_a', 'ox_sat'
EARTH_RADIUS = 6371  # in kilometers

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data')
ACROBAT_DIR = os.path.join(DATA_DIR, 'acrobat', 'transects', 'processed')

SAVE_DIR = os.path.join(SCRIPT_DIR, '..', f'visualization', 'contour_plots', 'wb', DATA_TYPE, '3D_plots')
INSET_MAP = os.path.join(SCRIPT_DIR, '..', f'visualization', 'maps', 'transects_wb.png')
SHORE_POINT = (-77.802938, 34.195220)

colormap_and_label = {
    'temp': (cmocean.cm.thermal, 'Temperature (°C)'),
    'salinity': (cmocean.cm.haline, 'Salinity (PSU)'),
    'density': (cmocean.cm.dense, 'Density (kg/m³)'),
    'turbidity': (cmocean.cm.turbid, 'Turbidity (NTU)'),
    'cdom': (cmocean.cm.matter, 'CDOM'),
    'chlor_a': (plt.cm.Greens, 'Chlorophyll a (µg/L)'),
    'ox_sat': (cmocean.cm.oxy, 'Oxygen Saturation (%)')
}

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return c * EARTH_RADIUS

global_min_values = {}
global_max_values = {}

def get_global_min_max(file_names):
    global_min = []
    global_max = []
    global_min_depth = []
    global_max_depth = []

    
    print(f"Processing global min/max {DATA_TYPE} values and depth...")
    for fname in tqdm(file_names):
        try:
            data = pd.read_csv(fname)
            global_min.append(data[DATA_TYPE].min())
            global_max.append(data[DATA_TYPE].max())
            global_min_depth.append(data['depth'].min())
            global_max_depth.append(data['depth'].max())
        except Exception as e:
            print(f"Error processing file {fname}: {e}")
    
    global_min_values[DATA_TYPE] = min(global_min)
    global_max_values[DATA_TYPE] = max(global_max)
    return min(global_min_depth), max(global_max_depth)


def plot_3D_transects(file_names, global_min, global_max, global_min_depth, global_max_depth, upto_idx):
    colormap, data_label = colormap_and_label[DATA_TYPE]
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    distances_from_shore = []
    
    dfs = []  # Store DataFrames after reading them
    for fname in file_names:
        df = pd.read_csv(fname)
        dfs.append(df)
        middle_idx = len(df) // 2
        middle_lat, middle_lon = df.iloc[middle_idx][['lat', 'lon']]
        distance_from_shore = haversine(SHORE_POINT[0], SHORE_POINT[1], middle_lon, middle_lat)
        distances_from_shore.append(distance_from_shore)
    
    sorted_files_and_dfs = sorted(zip(distances_from_shore, dfs, file_names))

    # Only loop through transects up to the specified index
    for idx, (distance, df, fname) in enumerate(sorted_files_and_dfs[:upto_idx + 1]):
        print(f"Interpolating and visualizing data for file: {fname}...")
        
        accumulated_distance = [0]

        # Modify this loop to calculate distance at every 10th data point
        for i in range(1, len(df)):
            if i % 10 == 0:
                lat1, lon1 = df.iloc[i - 10][['lat', 'lon']]
                lat2, lon2 = df.iloc[i][['lat', 'lon']]
                distance = haversine(lon1, lat1, lon2, lat2)
                accumulated_distance.append(accumulated_distance[-1] + distance)
            else:
                accumulated_distance.append(accumulated_distance[-1])  # Keep the same distance for non-10th points

        df['normalized_distance'] = accumulated_distance

        distance_from_shore = distances_from_shore[idx]  # Using the pre-calculated distance from shore

        # Print the calculated distance
        print(f"Distance from Shore for Transect {idx+1}: {distance_from_shore} km")

        # Interpolation
        yi = np.linspace(df['normalized_distance'].min(), df['normalized_distance'].max(), 100)
        zi = np.linspace(df['depth'].min(), df['depth'].max(), 100)
        yi, zi = np.meshgrid(yi, zi)

        xi = np.full(yi.shape, distance_from_shore) 

        colors = griddata((df['normalized_distance'], df['depth']), df[DATA_TYPE], (yi, zi), method=INTERPOLATION_METHOD)

        # Plotting
        ax.scatter(xi, yi, zi, c=colors.flatten(), cmap=colormap, marker='o', alpha=0.6, vmin=global_min, vmax=global_max)
        
    ax.set_xlabel('Distance from Shore (km)')
    ax.set_ylabel('Distance along transect (km)')
    ax.set_zlabel('Depth (m)')
    ax.set_xlim(2.5, 4.5)
    ax.set_ylim(ax.get_ylim())
    ax.set_zlim(global_max_depth, 0)
    sm = plt.cm.ScalarMappable(cmap=colormap, norm=LogNorm(vmin=0.1, vmax=5.5))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, ticks=np.linspace(0, 5.5, 12)) 
    cbar.set_label('Log10 of Chlorophyll a (µg/L)')

    axins = inset_axes(ax, width="30%", height="30%", loc='upper left')
    img = plt.imread(INSET_MAP)
    axins.imshow(img)
    axins.axis('off')

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    # Save the combined visualization for the current state
    combined_save_path = f"{SAVE_DIR}/upto_transect_{upto_idx + 1}.png"
    plt.savefig(combined_save_path, dpi=300)
    plt.close()  # Close the figure to free up memory

def create_gif(image_folder, gif_path, duration=1000):
    images = []
    for i in range(1, 8):
        file_path = os.path.join(image_folder, f'upto_transect_{i}.png')
        images.append(Image.open(file_path))

    images[0].save(gif_path, save_all=True, append_images=images[1:], optimize=False, duration=duration, loop=0)

def main():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    
    print("Loading transect data files...")
    file_names = [os.path.join(ACROBAT_DIR, f'transect_{i}.csv') for i in range(1, 8)]
    file_names = sorted(file_names, key=lambda x: int(x.split('_')[-1].split('.')[0]))

    global_min_depth, global_max_depth = get_global_min_max(file_names)
    for idx in range(len(file_names)):
        plot_3D_transects(file_names, global_min_values[DATA_TYPE], global_max_values[DATA_TYPE], global_min_depth, global_max_depth, idx)
    
    print(f"Global Minimum {DATA_TYPE}: {global_min_values[DATA_TYPE]}")
    print(f"Global Maximum {DATA_TYPE}: {global_max_values[DATA_TYPE]}")

    print("3D visualizations complete!")

    gif_save_path = os.path.join(SAVE_DIR, f'{DATA_TYPE}_gradient.gif')
    create_gif(SAVE_DIR, gif_save_path)

if __name__ == "__main__":
    main()