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
FILE_LIST = [
    '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/transect_1.xlsx',
    '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/transect_2.xlsx',
    '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/transect_3.xlsx',
    '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/transect_4.xlsx',
    '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/transect_5.xlsx',
    '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/transect_6.xlsx',
    '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/transect_7.xlsx'
]
SAVE_DIR = "/Users/mitchtork/HawkEye_Evaluation/visualization/maps/masonboro"

SATELLITE_IMAGES_DIR = "/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/crops"
SATELLITE_NAMES = ["HawkEye", "MODIS", "S3A", "S3B", "OLI8"]
SATELLITE_IMG_FILES = ["SEAHAWK1_HAWKEYE.2023050720230507.DLY.chlor_a.png", "AQUA_MODIS.2023050720230507.DLY.chlor_a.png", "S3A_OLCI_EFR.2023050720230507.DLY.chlor_a.png", "S3B_OLCI_EFR.2023050620230506.DLY.chlor_a.png", "LANDSAT8_OLI.2023050320230503.DLY.chlor_a.png"]
PIXEL_RESOLUTIONS_METERS = [120, 1000, 300, 300, 30]

SAT_IMG_BOUNDS = [34.1, 34.24, -77.85, -77.70]  # [min_lat, max_lat, min_lon, max_lon]

SUBPLOT_TITLES = [
    "RV Cape Fear, Masonboro Inlet - HawkEye (120m) from May 07, 2023",
    "RV Cape Fear, Masonboro Inlet - MODIS (1000m) from May 07, 2023",
    "RV Cape Fear, Masonboro Inlet - S3A (300m) from May 07, 2023",
    "RV Cape Fear, Masonboro Inlet - S3B (300m) from May 06, 2023",
    "RV Cape Fear, Masonboro Inlet - OLI8 (30m) from May 03, 2023"
]

COMPASS_ROSE_PATH = '/Users/mitchtork/HawkEye_Evaluation/python/helper_data/compass_rose.png'

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
    
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # Adjusting the subplot grid to 3x2 to accommodate 5 images
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(16, 24), subplot_kw={'projection': ccrs.PlateCarree()}, dpi=150)
    fig.patch.set_facecolor('#FAFAFA')  # Set the figure's background color to #FAFAFA

    axes = axes.flatten()
    plt.subplots_adjust(wspace=0.1, hspace=0.1)

    for i, (satellite_name, img_file, pixel_resolution_meters) in enumerate(zip(SATELLITE_NAMES, SATELLITE_IMG_FILES, PIXEL_RESOLUTIONS_METERS)):
        if i >= 5:  # Ensuring we don't go beyond the number of provided subplots
            break
        ax = axes[i]
        ax.set_facecolor('#FAFAFA')  # Set each subplot background color
        
        pixel_resolution_degrees = meters_to_degrees(pixel_resolution_meters, 34.1)

        satellite_img_path = os.path.join(SATELLITE_IMAGES_DIR, img_file)

        # Set the extent of the map to the bounds of the satellite image
        min_lat, max_lat, min_lon, max_lon = SAT_IMG_BOUNDS
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

        try:
            satellite_img = mpimg.imread(satellite_img_path)
            ax.imshow(satellite_img, extent=[min_lon, max_lon, min_lat, max_lat], transform=ccrs.PlateCarree(), origin='upper', aspect='auto')
        except FileNotFoundError:
            print(f"File not found: {satellite_img_path}")
            continue

        plot_transects(ax, dfs, colors)

        legend_handles = [Line2D([0], [0], color=colors[i], lw=2, label=f"Transect {i+1}") for i in range(n_colors)]
        ax.legend(handles=legend_handles, loc='upper right', title='Transect')

        # Set the title for each subplot from the SUBPLOT_TITLES list
        if i < len(SUBPLOT_TITLES):
            ax.set_title(SUBPLOT_TITLES[i])

        compass_rose_image = mpimg.imread(COMPASS_ROSE_PATH)
        compass_size = 0.02
        compass_position = (max_lon - 0.03, min_lat + 0.0125)
        ax.imshow(compass_rose_image, extent=[compass_position[0], compass_position[0] + compass_size, compass_position[1], compass_position[1] + compass_size], transform=ccrs.PlateCarree(), origin='upper')

        scale_bar_position = (compass_position[1] - 0.005, compass_position[0])
        draw_scale_bar(ax, scale_bar_position, length_km=2)

        # Set latitude and longitude tick marks
        ax.set_xticks([min_lon, max_lon], crs=ccrs.PlateCarree())
        ax.set_yticks([min_lat, max_lat], crs=ccrs.PlateCarree())
        lon_formatter = cticker.LongitudeFormatter()
        lat_formatter = cticker.LatitudeFormatter()
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)
        ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='both'))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='both'))

    # Optionally, hide the last subplot if not in use
    axes[-1].axis('off')

    plt.subplots_adjust(wspace=0.15)  # Adjust spacing between subplots
    mosaic_save_path = os.path.join(SAVE_DIR, "mosaic_map.png")
    plt.savefig(mosaic_save_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

if __name__ == '__main__':
    main()