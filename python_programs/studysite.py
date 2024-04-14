import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.image as mpimg
import geopandas as gpd
import os
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# Setup the base directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(SCRIPT_DIR, '..', 'visualization', 'maps', 'study_site_map.png')
COMPASS_ROSE_PATH = os.path.join(SCRIPT_DIR, 'local_processing_resources', 'compass_rose.png')
NATURAL_EARTH_DIR = os.path.join(SCRIPT_DIR, 'local_processing_resources', 'natural_earth')

# Set Cartopy to use local data
os.environ["CARTOPY_DATA_DIR"] = NATURAL_EARTH_DIR

STUDY_SITE_LON = -77.696587
STUDY_SITE_LAT = 34.193111

def draw_scale_bar(ax, location, length_km, color='black'):
    lat, lon = location
    length_deg = length_km / 111  # Conversion from km to degrees
    ax.plot([lon, lon + length_deg], [lat, lat], color=color, linewidth=0.5, transform=ccrs.PlateCarree())
    ax.plot([lon, lon], [lat, lat - 0.003], color=color, linewidth=0.5, transform=ccrs.PlateCarree())
    ax.plot([lon + length_deg, lon + length_deg], [lat, lat - 0.003], color=color, linewidth=0.5, transform=ccrs.PlateCarree())
    ax.text(lon, lat - 0.005, "0", va='top', ha='center', fontsize=5, transform=ccrs.PlateCarree())
    ax.text(lon + length_deg, lat - 0.005, f"{length_km} km", va='top', ha='center', fontsize=5, transform=ccrs.PlateCarree())

def set_map_extent(ax, width_in_degrees, height_in_degrees):
    min_lon = STUDY_SITE_LON - width_in_degrees / 2
    max_lon = STUDY_SITE_LON + width_in_degrees / 2
    min_lat = STUDY_SITE_LAT - height_in_degrees / 2
    max_lat = STUDY_SITE_LAT + height_in_degrees / 2
    ax.set_extent([min_lon, max_lon, min_lat, max_lat])

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

def plot_study_site():
    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent([STUDY_SITE_LON - 5, STUDY_SITE_LON + 5, STUDY_SITE_LAT - 5, STUDY_SITE_LAT + 5])

    # Define feature types and associated colors for coastline, land, and new layers
    feature_types = {
        'coastline': 'none',
        'land': '#c8c365',  # Land color
        'geography_marine_polys': '#a6cee3',  # Light blue for marine areas
        'geography_regions_polys': '#bdbdbd'  # Grey for geographic regions
    }

    # Load non-bathymetry features including new geography layers
    for feature_name in ['coastline', 'land', 'geography_marine_polys', 'geography_regions_polys']:
        shapefile_path = os.path.join(NATURAL_EARTH_DIR, f'ne_10m_{feature_name}', f'ne_10m_{feature_name}.shp')
        try:
            shape_feature = ShapelyFeature(Reader(shapefile_path).geometries(),
                                           ccrs.PlateCarree(), edgecolor='none',
                                           facecolor=feature_types[feature_name])
            ax.add_feature(shape_feature)
            print(f"Loaded {feature_name} successfully.")
        except Exception as e:
            print(f"Failed to load {feature_name}: {e}")

    # Bathymetry colors and files setup
    bathymetry_colors = [
        '#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6',
        '#4292c6', '#2171b5', '#08519c', '#08306b', '#042040',
        '#02132c', '#010b17'
    ]
    bathymetry_files = [
        'ne_10m_bathymetry_L_0', 'ne_10m_bathymetry_K_200', 'ne_10m_bathymetry_J_1000',
        'ne_10m_bathymetry_I_2000', 'ne_10m_bathymetry_H_3000', 'ne_10m_bathymetry_G_4000',
        'ne_10m_bathymetry_F_5000', 'ne_10m_bathymetry_E_6000', 'ne_10m_bathymetry_D_7000',
        'ne_10m_bathymetry_C_8000', 'ne_10m_bathymetry_B_9000', 'ne_10m_bathymetry_A_10000'
    ]

    # Load bathymetry files
    for file_name, color in zip(bathymetry_files, bathymetry_colors):
        shapefile_path = os.path.join(NATURAL_EARTH_DIR, 'ne_10m_bathymetry_all', f'{file_name}.shp')
        try:
            shape_feature = ShapelyFeature(Reader(shapefile_path).geometries(),
                                           ccrs.PlateCarree(), edgecolor='none',
                                           facecolor=color)
            ax.add_feature(shape_feature)
            print(f"Loaded {file_name} with color {color} successfully.")
        except Exception as e:
            print(f"Failed to load {file_name}: {e}")

    # Additional map setup
    plt.plot(STUDY_SITE_LON, STUDY_SITE_LAT, 'ro', transform=ccrs.PlateCarree(), label="R/V Cape Fear cruises")
    plt.legend(loc='lower right')
    plt.title("RV Cape Fear, May 03-05 2023, Wilmington, NC")
    compass_rose_image = mpimg.imread(COMPASS_ROSE_PATH)
    ax.imshow(compass_rose_image, extent=[STUDY_SITE_LON - 4.5, STUDY_SITE_LON - 3.0, STUDY_SITE_LAT + 3.0, STUDY_SITE_LAT + 4.5], transform=ccrs.PlateCarree(), zorder=10)

    draw_scale_bar(ax, (STUDY_SITE_LAT + 2.75, STUDY_SITE_LON - 4.25), 100, color='black')  # 100 km scale bar

    gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.savefig(SAVE_PATH, dpi=300, bbox_inches='tight')
    print(f"Map of study site plotted and saved to {SAVE_PATH}.")

if __name__ == "__main__":
    plot_study_site()


