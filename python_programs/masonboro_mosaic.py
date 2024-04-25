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
SATELLITE_IMAGES_DIR = os.path.join(DATA_DIR, 'sat_default', 'crops', 'chlor_a')
SAVE_DIR = os.path.join(SCRIPT_DIR, '..', 'visualization', 'maps')
os.makedirs(SAVE_DIR, exist_ok=True)

TRANSECTS = [os.path.join(ACROBAT_DIR, file) for file in os.listdir(ACROBAT_DIR) if file.startswith('transect_') and file.endswith('.csv')]
SATELLITE_IMGS = [file for file in os.listdir(SATELLITE_IMAGES_DIR) if file.endswith('.png')]

SUBPLOT_TITLES = [
    "RV Cape Fear, Masonboro Inlet - S3B-OLCI (120m) from May 03, 2023",
    "RV Cape Fear, Masonboro Inlet - S3A (300m) from May 04, 2023",
    "RV Cape Fear, Masonboro Inlet - S3B (300m) from May 06, 2023",
    "RV Cape Fear, Masonboro Inlet - S3A (300m) from May 03, 2023",
    "RV Cape Fear, Masonboro Inlet - MODIS (1000m) from May 07, 2023",
    "RV Cape Fear, Masonboro Inlet - SeaHawk-HawkEye (120m) from May 07, 2023",
    "RV Cape Fear, Masonboro Inlet - L8-OLI (30m) from May 03, 2023",
    "RV Cape Fear, Masonboro Inlet - S3B-OLCI 300m) from May 07, 2023",
    "RV Cape Fear, Masonboro Inlet - SeaHawk-HawkEye (120m) from May 06, 2023",
    "RV Cape Fear, Masonboro Inlet - S3A-OLCI (300m) from May 07, 2023"
]

SAT_IMG_BOUNDS = [34.10, 34.25, -77.85, -77.70]  # [min_lat, max_lat, min_lon, max_lon]

COMPASS_ROSE_PATH = os.path.join(SCRIPT_DIR, 'local_processing_resources', 'compass_rose.png')

# -----------------
# HELPER FUNCTIONS
# -----------------
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

def plot_transects(ax, dfs, colors):
    for i, df in enumerate(dfs):
        line = LineString(list(zip(df['lon'], df['lat'])))
        gdf = gpd.GeoDataFrame([1], geometry=[line], crs="EPSG:4326")
        gdf.plot(ax=ax, color=colors[i], linewidth=1)

def add_scale_bar(ax, length, location, linewidth=3):
    # Get the extent of the projected map
    x0, x1, y0, y1 = ax.get_extent()
    # Set the length of the scale bar
    scale_length = length / 111.32  # degrees per km at the equator (rough approximation)
    # Set the location
    x = x0 + (x1 - x0) * location[0]
    y = y0 + (y1 - y0) * location[1]
    # Draw the scale bar
    ax.plot([x, x - scale_length], [y, y], transform=ccrs.Geodetic(), color='black', linewidth=linewidth)
    # Label the scale bar
    ax.text(x - scale_length / 2, y - 0.005, f'{length} km', verticalalignment='top', horizontalalignment='center', transform=ccrs.Geodetic(), color='black')

# -----------------
# MAIN FUNCTION
# -----------------
def main():
    n_colors = len(TRANSECTS)
    colors = sns.color_palette("dark", n_colors=n_colors)

    dfs, _ = load_transect_data(TRANSECTS)
    
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # Dynamically determining the number of rows and columns for subplots
    n_cols = 3
    n_rows = (len(SATELLITE_IMGS) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(36, 8 * n_rows), subplot_kw={'projection': ccrs.PlateCarree()}, dpi=600)
    fig.patch.set_facecolor('#FAFAFA')
    axes = axes.flatten()

    for i, img_file in enumerate(SATELLITE_IMGS):
        ax = axes[i]
        ax.set_facecolor('#FAFAFA')
        
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

        ax.legend([Line2D([0], [0], color=color, lw=2) for color in colors], [f"Transect {j+1}" for j in range(n_colors)], loc='upper right', title='Transects')
        ax.set_title(SUBPLOT_TITLES[i])

        # Set the title for each subplot from the SUBPLOT_TITLES list
        if i < len(SUBPLOT_TITLES):
            ax.set_title(SUBPLOT_TITLES[i])

        compass_rose_image = mpimg.imread(COMPASS_ROSE_PATH)
        compass_size = 0.02
        compass_position = (max_lon - 0.03, min_lat + 0.0125)
        ax.imshow(compass_rose_image, extent=[compass_position[0], compass_position[0] + compass_size, compass_position[1], compass_position[1] + compass_size], transform=ccrs.PlateCarree(), origin='upper')

        scale_bar_position = (compass_position[1] - 0.005, compass_position[0])
        add_scale_bar(ax, 2, location=scale_bar_position)

        # Set latitude and longitude tick marks
        ax.set_xticks([min_lon, max_lon], crs=ccrs.PlateCarree())
        ax.set_yticks([min_lat, max_lat], crs=ccrs.PlateCarree())
        lon_formatter = cticker.LongitudeFormatter()
        lat_formatter = cticker.LatitudeFormatter()
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)
        ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='both'))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='both'))

    # Hide unused subplots if there are any
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    # Adjust subplot parameters to reduce white space
    plt.subplots_adjust(wspace=-0.5, hspace=0.2)

    plt.savefig(os.path.join(SAVE_DIR, "mosaic_masonboro.png"), dpi=300, bbox_inches='tight')
    plt.close(fig)

if __name__ == '__main__':
    main()