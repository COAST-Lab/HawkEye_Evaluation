# Script Name: Transects Visualization
# Author: Mitch Torkelson
# Date: August 2023

# Description:
# This script visualizes the transect data from multiple Excel files on a map. 
# The transects are represented as line segments on a basemap, with various features
# like gridlines, scale bars, and a compass rose added for context. 
# The resulting map is saved as an PNG to the desingated folder.


# -----------------
# IMPORTS
# -----------------
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.image as mpimg
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import contextily as ctx
import os
from matplotlib.lines import Line2D
import seaborn as sns

# -----------------
# CONSTANTS
# -----------------
FILE_LIST = [
    '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/transect_1.xlsx',
    '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/transect_2.xlsx',
    '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/transect_3.xlsx',
    '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/transect_4.xlsx',
    '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/transect_5.xlsx',
    '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/transect_6.xlsx',
    '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/transect_7.xlsx'
]
SAVE_DIR = "/Users/mitchtork/HawkEye_Evaluation/visualization/maps/transects_wb.png"
COMPASS_ROSE_PATH = '/Users/mitchtork/HawkEye_Evaluation/python/helper_data/compass_rose.png'

# -----------------
# HELPER FUNCTIONS
# -----------------
def load_transect_data(files):
    try:
        dfs = [pd.read_excel(file).apply(pd.to_numeric, errors='coerce').dropna(subset=['long', 'lat']) for file in files]
        combined_df = pd.concat(dfs, ignore_index=True)
        return dfs, combined_df
    except Exception as e:
        print(f"An error occurred while loading transect data: {e}")
        return [], pd.DataFrame()

# Calculate the bounds of the map based on the transect data
def calculate_bounds(dfs, margin=0.05):
    total_bounds = gpd.GeoDataFrame(dfs, geometry=gpd.points_from_xy(dfs.long, dfs.lat)).total_bounds
    min_lon, min_lat, max_lon, max_lat = total_bounds
    min_lon -= margin
    max_lon += margin
    min_lat -= margin
    max_lat += margin
    return min_lon, max_lon, min_lat, max_lat

def plot_transects(ax, dfs, colors):
    for i, df in enumerate(dfs):
        line = LineString(list(zip(df['long'], df['lat'])))
        gdf = gpd.GeoDataFrame([1], geometry=[line], crs="EPSG:4326")
        gdf.plot(ax=ax, color=colors[i], linewidth=1)

def draw_scale_bar(ax, location, length_km, color='black'):
    lat, lon = location
    length_deg = length_km / 111  # Conversion from km to degrees
    half_length_deg = length_deg / 2  # Midpoint for the minor tick

    ax.plot([lon, lon + length_deg], [lat, lat], color=color, linewidth=0.5, transform=ccrs.PlateCarree())

    ax.plot([lon, lon], [lat, lat - 0.003], color=color, linewidth=0.5, transform=ccrs.PlateCarree())
    ax.plot([lon + length_deg, lon + length_deg], [lat, lat - 0.003], color=color, linewidth=0.5, transform=ccrs.PlateCarree())

    ax.plot([lon + half_length_deg, lon + half_length_deg], [lat, lat - 0.002], color=color, linewidth=0.4, transform=ccrs.PlateCarree())

    ax.text(lon, lat - 0.005, "0", va='top', ha='center', fontsize=5, transform=ccrs.PlateCarree())
    ax.text(lon + length_deg, lat - 0.005, f"{length_km} km", va='top', ha='center', fontsize=5, transform=ccrs.PlateCarree())


# -----------------
# MAIN FUNCTION
# -----------------
def main():
    n_colors = len(FILE_LIST)
    colors = sns.color_palette("dark", n_colors=n_colors)

    dfs, combined_dfs = load_transect_data(FILE_LIST)
    min_lon, max_lon, min_lat, max_lat = calculate_bounds(combined_dfs)

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

    # Set the blank space around the plot to #FAFAFA
    fig.patch.set_facecolor('#FAFAFA')
    ax.set_facecolor('#FAFAFA')

    plot_transects(ax, dfs, colors)

    legend_handles = [Line2D([0], [0], color=colors[i], lw=2, label=f"Transect {i+1}") for i in range(n_colors)]
    ax.legend(handles=legend_handles, loc='upper right', title='Transect')

    # Gridlines and labels for lat/lon ticks
    grid_lines = ax.gridlines(draw_labels=True, zorder=1, linestyle='--', linewidth=0.5)
    grid_lines.xlines = True
    grid_lines.ylines = True
    plt.grid(which='both', linestyle='--', linewidth=0.5, zorder=1)

    # Map title
    plt.title("RV Cape Fear, May 05 2023, Wilmington, NC")

    # Compass rose (bottom right corner of map)
    compass_rose_image = mpimg.imread('/Users/mitchtork/HawkEye_Evaluation/python/helper_data/compass_rose.png')
    compass_position = (max_lon - 0.03, min_lat + 0.0125)  # Positioned near bottom right
    compass_size = 0.02
    ax.imshow(compass_rose_image, extent=[compass_position[0], compass_position[0] + compass_size, compass_position[1], compass_position[1] + compass_size], transform=ccrs.PlateCarree(), zorder=10)

    # Draw scale bar (below compass rose)
    scale_bar_location = (min_lat + 0.01, max_lon - 0.029)  # Positioned below compass rose
    draw_scale_bar(ax, scale_bar_location, 2)  # Major ticks at 0 and 1

    # Add basemap for context (OpenStreetMap)
    ctx.add_basemap(ax, crs=ccrs.PlateCarree(), source=ctx.providers.OpenStreetMap.Mapnik)

    # Save the map figure and display it
    if not os.path.exists(os.path.dirname(SAVE_DIR)):
        os.makedirs(os.path.dirname(SAVE_DIR))
    plt.savefig(SAVE_DIR, dpi=300, bbox_inches='tight')
    print(f"Map of transects plotted and saved to {SAVE_DIR}.")

# -----------------
# SCRIPT EXECUTION
# -----------------
if __name__ == '__main__':
    main()