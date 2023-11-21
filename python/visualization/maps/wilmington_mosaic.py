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
    '/Users/macbook/thesis_materials/data/acrobat/050523/transects/cleaned_data/cleaned_data_transect_1.xlsx',
    '/Users/macbook/thesis_materials/data/acrobat/050523/transects/cleaned_data/cleaned_data_transect_2.xlsx',
    '/Users/macbook/thesis_materials/data/acrobat/050523/transects/cleaned_data/cleaned_data_transect_3.xlsx',
    '/Users/macbook/thesis_materials/data/acrobat/050523/transects/cleaned_data/cleaned_data_transect_4.xlsx',
    '/Users/macbook/thesis_materials/data/acrobat/050523/transects/cleaned_data/cleaned_data_transect_5.xlsx',
    '/Users/macbook/thesis_materials/data/acrobat/050523/transects/cleaned_data/cleaned_data_transect_6.xlsx',
    '/Users/macbook/thesis_materials/data/acrobat/050523/transects/cleaned_data/cleaned_data_transect_7.xlsx'
]
SAVE_DIR = "/Users/macbook/thesis_materials/visualization/maps/wilmington"

SATELLITE_IMAGES_DIR = "/Users/macbook/thesis_materials/data/satellite_matchups_mod/locations/wilmington/products/chlor/crops"
SATELLITE_NAMES = ["HawkEye", "MODIS", "S3A", "S3B"]
SATELLITE_IMG_FILES = ["SEAHAWK1_HAWKEYE.2023050720230507.chlor_a-mean_crop.png", "AQUA_MODIS.2023050720230507.chlor_a-mean_crop.png", "S3A_OLCI_EFRNT.2023050720230507.chlor_a-mean_crop.png", "S3B_OLCI_EFR.2023050620230506.chlor_a-mean_crop.png"]
PIXEL_RESOLUTIONS_METERS = [120, 1000, 300, 300]
SAT_IMG_BOUNDS = [33.75, 34.5, -78.25, -77.50]  # [min_lat, max_lat, min_lon, max_lon]

SUBPLOT_TITLES = [
    "RV Cape Fear, Wilmington - HawkEye (120m) from  May 07, 2023",
    "RV Cape Fear, Wilmington - MODIS (1000m) from  May 07, 2023",
    "RV Cape Fear, Wilmington - S3A (300m) from  May 07, 2023",
    "RV Cape Fear, Wilmington - S3B (300m) from May 06, 2023"
]

COMPASS_ROSE_PATH = '/Users/macbook/thesis_materials/python/helper_data/compass_rose.png'

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

    # Create a mosaic figure with subplots for each satellite image
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 16), subplot_kw={'projection': ccrs.PlateCarree()}, dpi=150)  # Adjust nrows and ncols based on the number of images
    axes = axes.flatten()

    # Adjust spacing between subplots
    plt.subplots_adjust(wspace=0.1, hspace=0.1)

    for i, (satellite_name, img_file, pixel_resolution_meters) in enumerate(zip(SATELLITE_NAMES, SATELLITE_IMG_FILES, PIXEL_RESOLUTIONS_METERS)):
        ax = axes[i]
        
        pixel_resolution_degrees = meters_to_degrees(pixel_resolution_meters, 34.1)

        satellite_img_path = os.path.join(SATELLITE_IMAGES_DIR, img_file)

        # Set the extent of the map to the bounds of the satellite image
        min_lat, max_lat, min_lon, max_lon = SAT_IMG_BOUNDS
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

        # Read and display the satellite image
        satellite_img = mpimg.imread(satellite_img_path)

        # Check if the image size is too large
        if satellite_img.shape[0] > 65536 or satellite_img.shape[1] > 65536:
            print(f"Warning: Image '{img_file}' is too large and may not display correctly.")
            continue

        ax.imshow(satellite_img, extent=[min_lon, max_lon, min_lat, max_lat], transform=ccrs.PlateCarree(), origin='upper', aspect='auto')

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

    # Adjust the spacing between columns
    plt.subplots_adjust(wspace=0.15)

    # Adjust save path for the mosaic
    mosaic_save_path = os.path.join(SAVE_DIR, "mosaic_map.png")
    plt.savefig(mosaic_save_path, dpi=300, bbox_inches='tight')

    # Close the mosaic figure
    plt.close(fig)

# -----------------
# SCRIPT EXECUTION
# -----------------
if __name__ == '__main__':
    main()