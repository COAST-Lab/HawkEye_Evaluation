# -----------------
# IMPORTS
# -----------------
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.image as mpimg
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import os
from matplotlib.lines import Line2D
import seaborn as sns
import cartopy.mpl.ticker as cticker
import matplotlib.ticker as mticker


# -----------------
# CONSTANTS
# -----------------
SELECTED_DATA_TYPE = 'chlor_a'  # Change this to 'chlor_a' as needed

BASE_DIR = '/Users/macbook/HawkEye_Evaluation'
TRANSECT_DIR = os.path.join(BASE_DIR, 'data/acrobat/050523/transects/processed_transects')
FILE_LIST = [os.path.join(TRANSECT_DIR, f) for f in os.listdir(TRANSECT_DIR) if f.endswith('.xlsx')]
SATELLITE_IMAGES_DIR = os.path.join(BASE_DIR, f'data/satellite_matchups/locations/masonboro/_products/{SELECTED_DATA_TYPE}/crops')
SATELLITE_IMG_FILES = sorted([f for f in os.listdir(SATELLITE_IMAGES_DIR) if f.endswith('.png')])
SATELLITE_NAMES = ["MODIS", "S3A", "S3B", "HawkEye"]  # Ensure this list is in the same order as SATELLITE_IMG_FILES
PIXEL_RESOLUTIONS_METERS = [120, 1000, 300, 3]
SAT_IMG_BOUNDS = [34.1, 34.24, -77.85, -77.70]  # [min_lat, max_lat, min_lon, max_lon]
COMPASS_ROSE_PATH = os.path.join(BASE_DIR, 'python/helper_data/compass_rose.png')
SAVE_DIR = os.path.join(BASE_DIR, f'visualization/maps/masonboro/{SELECTED_DATA_TYPE}')

# Ensure SUBPLOT_TITLES align with SATELLITE_NAMES and SATELLITE_IMG_FILES
SUBPLOT_TITLES = [
    "RV Cape Fear, Masonboro Inlet - MODIS (1000m) from May 07, 2023",
    "RV Cape Fear, Masonboro Inlet - S3A (300m) from May 07, 2023",
    "RV Cape Fear, Masonboro Inlet - S3B (300m) from May 06, 2023",
    "RV Cape Fear, Masonboro Inlet - HawkEye (120m) from May 07, 2023"
]

# -----------------
# HELPER FUNCTIONS
# -----------------
def meters_to_degrees(meters, latitude):
    meters_per_degree = 111000  # Approximate conversion at given latitude
    return meters / meters_per_degree

def load_transect_data(files):
    try:
        dfs = [pd.read_excel(file).apply(pd.to_numeric, errors='coerce').dropna(subset=['long', 'lat']) for file in files]
        combined_df = pd.concat(dfs, ignore_index=True)
        return dfs, combined_df
    except Exception as e:
        print(f"An error occurred while loading transect data: {e}")
        return [], pd.DataFrame()

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
    
    # Create the save directory if it doesn't exist
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # Create and save individual plots
    for i, img_file in enumerate(SATELLITE_IMG_FILES):
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': ccrs.PlateCarree()}, dpi=150)
        
        satellite_name = SATELLITE_NAMES[i]
        subplot_title = SUBPLOT_TITLES[i]
        satellite_img_path = os.path.join(SATELLITE_IMAGES_DIR, img_file)

        pixel_resolution_degrees = meters_to_degrees(PIXEL_RESOLUTIONS_METERS[i], 34.1)
        min_lat, max_lat, min_lon, max_lon = SAT_IMG_BOUNDS
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

        satellite_img = mpimg.imread(satellite_img_path)
        ax.imshow(satellite_img, extent=[min_lon, max_lon, min_lat, max_lat], transform=ccrs.PlateCarree(), origin='upper', aspect='auto')

        plot_transects(ax, dfs, colors)
        legend_handles = [Line2D([0], [0], color=colors[i], lw=2, label=f"Transect {i+1}") for i in range(n_colors)]
        ax.legend(handles=legend_handles, loc='upper right', title='Transect')

        ax.set_title(subplot_title)

        compass_rose_image = mpimg.imread(COMPASS_ROSE_PATH)
        compass_size = 0.02
        compass_position = (max_lon - 0.03, min_lat + 0.0125)
        ax.imshow(compass_rose_image, extent=[compass_position[0], compass_position[0] + compass_size, compass_position[1], compass_position[1] + compass_size], transform=ccrs.PlateCarree(), origin='upper')

        scale_bar_position = (compass_position[1] - 0.005, compass_position[0])
        draw_scale_bar(ax, scale_bar_position, length_km=2)

        ax.set_xticks([min_lon, max_lon], crs=ccrs.PlateCarree())
        ax.set_yticks([min_lat, max_lat], crs=ccrs.PlateCarree())
        lon_formatter = cticker.LongitudeFormatter()
        lat_formatter = cticker.LatitudeFormatter()
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)
        ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='both'))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='both'))

        individual_plot_save_path = os.path.join(SAVE_DIR, f"{satellite_name}_map.png")
        plt.savefig(individual_plot_save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)

    # Create a mosaic figure with subplots for each satellite image
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 16), subplot_kw={'projection': ccrs.PlateCarree()}, dpi=150)
    axes = axes.flatten()

    for i, img_file in enumerate(SATELLITE_IMG_FILES):
        ax = axes[i]
        satellite_name = SATELLITE_NAMES[i]
        subplot_title = SUBPLOT_TITLES[i]
        satellite_img_path = os.path.join(SATELLITE_IMAGES_DIR, img_file)

        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
        satellite_img = mpimg.imread(satellite_img_path)
        ax.imshow(satellite_img, extent=[min_lon, max_lon, min_lat, max_lat], transform=ccrs.PlateCarree(), origin='upper', aspect='auto')

        plot_transects(ax, dfs, colors)
        ax.legend(handles=legend_handles, loc='upper right', title='Transect')
        ax.set_title(subplot_title)

        ax.imshow(compass_rose_image, extent=[compass_position[0], compass_position[0] + compass_size, compass_position[1], compass_position[1] + compass_size], transform=ccrs.PlateCarree(), origin='upper')
        draw_scale_bar(ax, scale_bar_position, length_km=2)

        ax.set_xticks([min_lon, max_lon], crs=ccrs.PlateCarree())
        ax.set_yticks([min_lat, max_lat], crs=ccrs.PlateCarree())
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)
        ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='both'))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='both'))

    plt.subplots_adjust(wspace=0.15, hspace=0.1)
    mosaic_save_path = os.path.join(SAVE_DIR, "mosaic_map.png")
    plt.savefig(mosaic_save_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

# -----------------
# SCRIPT EXECUTION
# -----------------
if __name__ == '__main__':
    main()
