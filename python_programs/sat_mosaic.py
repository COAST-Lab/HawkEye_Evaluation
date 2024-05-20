import os
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import LineString
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cartopy.crs as ccrs
from matplotlib.lines import Line2D
import seaborn as sns
import cartopy.mpl.ticker as cticker
import matplotlib.ticker as mticker

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data')
ACROBAT_DIR = os.path.join(DATA_DIR, 'acrobat', 'transects', 'processed')
SATELLITE_IMAGES_DIR = os.path.join(DATA_DIR, 'sat_default', 'crops', 'chl')
SAVE_DIR = os.path.join(SCRIPT_DIR, '..', 'visualization', 'maps')
os.makedirs(SAVE_DIR, exist_ok=True)

TRANSECTS = [os.path.join(ACROBAT_DIR, file) for file in os.listdir(ACROBAT_DIR) if file.startswith('transect_') and file.endswith('.csv')]
SATELLITE_IMGS = [file for file in os.listdir(SATELLITE_IMAGES_DIR) if file.endswith('.png')]

SUBPLOT_TITLES = [
    "Chl - MODIS (1000m) from May 07, 2023",
    "Chl - SeaHawk-HawkEye (120m) from May 07, 2023",
    "Chl - S3A-OLCI (300m) from May 07, 2023",
    "Chl - S3B-OLCI (300m) from May 07, 2023"
]

SAT_IMG_BOUNDS = [34.10, 34.25, -77.85, -77.70]  # [min_lat, max_lat, min_lon, max_lon]
COMPASS_ROSE_PATH = os.path.join(SCRIPT_DIR, 'local_processing_resources', 'compass_rose.png')

def meters_to_degrees(meters, latitude):
    return meters / (111000 * np.cos(np.radians(latitude)))

def load_transect_data(files):
    try:
        dfs = [pd.read_csv(file).apply(pd.to_numeric, errors='coerce').dropna(subset=['lon', 'lat']) for file in files]
        combined_df = pd.concat(dfs, ignore_index=True)
        return dfs, combined_df
    except Exception as e:
        print(f"An error occurred while loading transect data: {e}")
        return [], pd.DataFrame()

def plot_transects(ax, dfs, color='red'):
    for df in dfs:
        line = LineString(list(zip(df['lon'], df['lat'])))
        gdf = gpd.GeoDataFrame([1], geometry=[line], crs="EPSG:4326")
        gdf.plot(ax=ax, color=color, linewidth=1)

def add_scale_bar(ax, length_km, location=(0.05, 0.25), linewidth=1, color='black', fontsize=6):
    # Convert length in kilometers to degrees (approximation)
    length_deg = length_km / 111.32  # Rough conversion factor for degrees to kilometers at the equator
    x0, x1, y0, y1 = ax.get_extent()
    x = x0 + (x1 - x0) * location[0]
    y = y0 + (y1 - y0) * location[1]
    ax.plot([x, x + length_deg], [y, y], transform=ccrs.Geodetic(), color=color, linewidth=linewidth)
    ax.text(x + length_deg / 2, y - 0.001, f'{length_km} km', verticalalignment='top', horizontalalignment='center', transform=ccrs.Geodetic(), color=color, fontsize=fontsize)

def main():
    dfs, _ = load_transect_data(TRANSECTS)

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    may_7_images = [img for img, title in zip(SATELLITE_IMGS, SUBPLOT_TITLES) if "May 07, 2023" in title]

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 20), subplot_kw={'projection': ccrs.PlateCarree()})
    fig.patch.set_facecolor('#FFFFFF')

    axes = axes.flatten()

    # Desired order for images: MODIS, Hawkeye, S3B, S3A
    #order = [3, 2, 0, 1]  # for kd490
    order = [0, 1, 3, 2]  # for chlor_a
    for i, idx in enumerate(order):
        ax = axes[i]
        ax.set_facecolor('#FFFFFF')

        satellite_img_path = os.path.join(SATELLITE_IMAGES_DIR, may_7_images[idx])

        min_lat, max_lat, min_lon, max_lon = SAT_IMG_BOUNDS
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

        try:
            satellite_img = mpimg.imread(satellite_img_path)
            ax.imshow(satellite_img, extent=[min_lon, max_lon, min_lat, max_lat], transform=ccrs.PlateCarree(), origin='upper', aspect='auto')
        except FileNotFoundError:
            print(f"File not found: {satellite_img_path}")
            continue

        plot_transects(ax, dfs, 'red')
        ax.set_title(SUBPLOT_TITLES[i])

        compass_rose_image = mpimg.imread(COMPASS_ROSE_PATH)
        compass_size = 0.02  # Define the size of the compass rose
        # Calculate position for compass rose similar to scale bar
        x0, x1, y0, y1 = ax.get_extent()
        compass_x = x1 - (x1 - x0) * 0.207
        compass_y = y0 + (y1 - y0) * 0.07
        ax.imshow(compass_rose_image, extent=[compass_x, compass_x + compass_size, compass_y, compass_y + compass_size], transform=ccrs.PlateCarree(), origin='upper')
        add_scale_bar(ax, length_km=2, location=(0.8, 0.05), linewidth=2, color='black', fontsize=12)

        # Set latitude and longitude tick marks
        ax.set_xticks(np.linspace(min_lon, max_lon, num=5), crs=ccrs.PlateCarree())
        ax.set_yticks(np.linspace(min_lat, max_lat, num=5), crs=ccrs.PlateCarree())
        lon_formatter = cticker.LongitudeFormatter()
        lat_formatter = cticker.LatitudeFormatter()
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)

    # Hide unused subplots if there are any
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    plt.subplots_adjust(wspace=0.15, hspace=0.15)
    plt.savefig(os.path.join(SAVE_DIR, "mosaic_masonboro_chl.png"), dpi=500, bbox_inches='tight')  # Adjusted dpi
    plt.close(fig)

if __name__ == '__main__':
    main()
