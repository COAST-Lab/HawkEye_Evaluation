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
BASE_DIR = "/Users/macbook/thesis_materials"
COMPASS_ROSE_PATH = '/Users/macbook/thesis_materials/python/helper_data/compass_rose.png'
FILE_LIST = [
    '/Users/macbook/thesis_materials/data/acrobat/050523/transects/cleaned_data/cleaned_data_transect_1.xlsx',
    '/Users/macbook/thesis_materials/data/acrobat/050523/transects/cleaned_data/cleaned_data_transect_2.xlsx',
    '/Users/macbook/thesis_materials/data/acrobat/050523/transects/cleaned_data/cleaned_data_transect_3.xlsx',
    '/Users/macbook/thesis_materials/data/acrobat/050523/transects/cleaned_data/cleaned_data_transect_4.xlsx',
    '/Users/macbook/thesis_materials/data/acrobat/050523/transects/cleaned_data/cleaned_data_transect_5.xlsx',
    '/Users/macbook/thesis_materials/data/acrobat/050523/transects/cleaned_data/cleaned_data_transect_6.xlsx',
    '/Users/macbook/thesis_materials/data/acrobat/050523/transects/cleaned_data/cleaned_data_transect_7.xlsx'
]
SATELLITE_NAMES = ["HawkEye", "MODIS", "S3A", "S3B"]
SATELLITE_IMG_FILES = [
    "SEAHAWK1_HAWKEYE.2023050720230507.chlor_a-mean_crop.png",
    "AQUA_MODIS.2023050720230507.chlor_a-mean_crop.png",
    "S3A_OLCI_EFRNT.2023050720230507.chlor_a-mean_crop.png",
    "S3B_OLCI_EFR.2023050620230506.chlor_a-mean_crop.png"
    ]

PIXEL_RESOLUTIONS_METERS = [120, 1000, 300, 300]

# locations dictionary
LOCATIONS = {
    "masonboro": {
        "save_dir": f"{BASE_DIR}/visualization/maps/masonboro",
        "sat_img_bounds": [34.10, 34.25, -77.85, -77.70],
        "subplot_titles": [
            "RV Cape Fear, May 07 2023, 15:09:55 EST, Masonboro Inlet - HawkEye (120m)",
            "RV Cape Fear, May 07 2023, 18:45:01 EST, Masonboro Inlet - MODIS (1000m)",
            "RV Cape Fear, May 07 2023, 15:34:21 EST, Masonboro Inlet - S3A (300m)",
            "RV Cape Fear, May 06 2023, 15:21:10 EST, Masonboro Inlet - S3B (300m)"
        ]
    },
    "wilmington": {
        "save_dir": f"{BASE_DIR}/visualization/maps/wilmington",
        "sat_img_bounds": [33.75, 34.5, -78.25, -77.50],
        "subplot_titles": [
            "RV Cape Fear, May 07 2023, 15:09:55 EST, Wilmington, NC - HawkEye (120m)",
            "RV Cape Fear, May 07 2023, 18:45:01 EST, Wilmington, NC - MODIS (1000m)",
            "RV Cape Fear, May 07 2023, 15:34:21 EST, Wilmington, NC - S3A (300m)",
            "RV Cape Fear, May 06 2023, 15:21:10 EST, Wilmington, NC - S3B (300m)"
        ]
    },
    "onslowbay": {
        "save_dir": f"{BASE_DIR}/visualization/maps/onslowbay",
        "sat_img_bounds": [33, 36, -79, -76],
        "subplot_titles": [
            "RV Cape Fear, May 07 2023, 15:09:55 EST, Onslow Bay - HawkEye (120m)",
            "RV Cape Fear, May 07 2023, 18:45:01 EST, Onslow Bay - MODIS (1000m)",
            "RV Cape Fear, May 07 2023, 15:34:21 EST, Onslow Bay - S3A (300m)",
            "RV Cape Fear, May 06 2023, 15:21:10 EST, Onslow Bay - S3B (300m)"
        ]
    }
}


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

def setup_lat_lon_labels(ax, pixel_resolution_degrees):
    lon_formatter = cticker.LongitudeFormatter()
    lat_formatter = cticker.LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(pixel_resolution_degrees))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(pixel_resolution_degrees))

def add_compass_rose(ax, compass_rose_path, location=(0.05, 0.05), size=(0.1, 0.1)):
    img = mpimg.imread(compass_rose_path)
    x0, y0 = location
    width, height = size
    ax.figure.figimage(img, xo=x0 * ax.figure.bbox.width, yo=y0 * ax.figure.bbox.height, origin='lower', zorder=1, resize=True)
    ax.set_xlim(ax.get_xlim()[0], ax.get_xlim()[1] + width)

# -----------------
# MAIN FUNCTION
# -----------------
def main(location):
    if location not in LOCATIONS:
        print(f"Invalid location: {location}. Please choose from 'masonboro', 'wilmington', or 'onslowbay'.")
        return

    location_data = LOCATIONS[location]

    # Update variables based on the chosen location
    save_dir = location_data["save_dir"]
    sat_img_bounds = location_data["sat_img_bounds"]
    subplot_titles = location_data["subplot_titles"]
    satellite_images_dir = f"/Users/macbook/thesis_materials/data/satellite_matchups_mod/locations/{location}/products/chlor/crops"
    
    n_colors = len(FILE_LIST)
    colors = sns.color_palette("dark", n_colors=n_colors)

    dfs, combined_dfs = load_transect_data(FILE_LIST)
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 16), subplot_kw={'projection': ccrs.PlateCarree()}, dpi=150)
    axes = axes.flatten()
    plt.subplots_adjust(wspace=0.1, hspace=0.1)

    for i, (satellite_name, img_file, pixel_resolution_meters) in enumerate(zip(SATELLITE_NAMES, SATELLITE_IMG_FILES, PIXEL_RESOLUTIONS_METERS)):
        ax = axes[i]
        pixel_resolution_degrees = meters_to_degrees(pixel_resolution_meters, 34.1)
        satellite_img_path = os.path.join(satellite_images_dir, img_file)

        # Check if the satellite image file exists
        if not os.path.exists(satellite_img_path):
            print(f"Warning: Image file '{satellite_img_path}' not found.")
            continue

        min_lat, max_lat, min_lon, max_lon = sat_img_bounds
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

        satellite_img = mpimg.imread(satellite_img_path)
        if satellite_img.shape[0] > 65536 or satellite_img.shape[1] > 65536:
            print(f"Warning: Image '{img_file}' is too large and may not display correctly.")
            continue

        ax.imshow(satellite_img, extent=[min_lon, max_lon, min_lat, max_lat], transform=ccrs.PlateCarree(), origin='upper', aspect='auto')
        plot_transects(ax, dfs, colors)

        ax.set_title(subplot_titles[i], fontsize=12, fontweight='bold', loc='left', style='italic')
        ax.grid(True)

        setup_lat_lon_labels(ax, pixel_resolution_degrees)

        if i == 3:
            add_compass_rose(ax, COMPASS_ROSE_PATH)

    plt.savefig(os.path.join(save_dir, f"{location}_chlor_a_satellite_transects.png"), dpi=150)
    plt.show()


# -----------------
# SCRIPT EXECUTION
# -----------------
if __name__ == "__main__":
    selected_location = input("Enter location (masonboro, wilmington, or onslowbay): ").strip().lower()
    main(selected_location)