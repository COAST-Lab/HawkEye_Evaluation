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
   '/Users/macbook/thesis_materials/data/acrobat/050323/transects/transect_1.xlsx'
]
SAVE_DIR = "/Users/macbook/thesis_materials/visualization/maps/transects_cf.png"
COMPASS_ROSE_PATH = '/Users/macbook/thesis_materials/python/helper_images/compass_rose.png'


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
def calculate_bounds(combined_df, margin=0.05):
    geodf = gpd.GeoDataFrame(combined_df, geometry=gpd.points_from_xy(combined_df.long, combined_df.lat))
    min_lon, min_lat, max_lon, max_lat = geodf.geometry.total_bounds
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
    # Color selection for only one transect
    color = sns.color_palette("dark", n_colors=1)[0]

    dfs, combined_dfs = load_transect_data(FILE_LIST)
    min_lon, max_lon, min_lat, max_lat = calculate_bounds(combined_dfs)

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent([min_lon, max_lon, min_lat, max_lat])
    plot_transects(ax, dfs, [color])

    # Legend for just one transect
    legend_handle = Line2D([0], [0], color=color, lw=2, label="Transect 1")
    ax.legend(handles=[legend_handle], loc='upper right', title='Transect')

    # Gridlines and labels for lat/lon ticks
    grid_lines = ax.gridlines(draw_labels=True, zorder=1, linestyle='--', linewidth=0.5)
    grid_lines.xlines = True
    grid_lines.ylines = True
    plt.grid(which='both', linestyle='--', linewidth=0.5, zorder=1)

    # Map title
    plt.title("RV Cape Fear, May 03 2023, Wilmington, NC")

    # Compass rose (bottom right corner of map)
    compass_rose_image = mpimg.imread('/Users/macbook/python_programs/thesis/images/compass_rose.png')
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
    plt.show()
    print(f"Map of transects plotted and saved to {SAVE_DIR}.")


# -----------------
# SCRIPT EXECUTION
# -----------------
if __name__ == '__main__':
    main()
