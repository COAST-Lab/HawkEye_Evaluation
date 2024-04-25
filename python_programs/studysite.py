import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.image as mpimg
import os
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm

# Setup the base directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(SCRIPT_DIR, '..', 'visualization', 'maps', 'study_site_map.png')
COMPASS_ROSE_PATH = os.path.join(SCRIPT_DIR, 'local_processing_resources', 'compass_rose.png')
NATURAL_EARTH_DIR = os.path.join(SCRIPT_DIR, 'local_processing_resources', 'natural_earth')

# Set Cartopy to use local data
os.environ["CARTOPY_DATA_DIR"] = NATURAL_EARTH_DIR

STUDY_SITE_LON = -77.696587
STUDY_SITE_LAT = 34.193111

def add_scale_bar(ax, length_km, location=(0.940, 0.075), linewidth=1, color='black', fontsize=6):
    # Convert length in kilometers to degrees (approximation)
    length_deg = length_km / 111.32
    x0, x1, y0, y1 = ax.get_extent()
    x = x0 + (x1 - x0) * location[0]
    y = y0 + (y1 - y0) * location[1]
    ax.plot([x, x + length_deg], [y, y], transform=ccrs.Geodetic(), color=color, linewidth=linewidth)
    ax.text(x + length_deg / 2, y - 0.05, f'{length_km} km', verticalalignment='top', horizontalalignment='center', transform=ccrs.Geodetic(), color=color, fontsize=fontsize)

def set_map_extent(ax, width_in_degrees, height_in_degrees):
    min_lon = STUDY_SITE_LON - width_in_degrees / 2
    max_lon = STUDY_SITE_LON + width_in_degrees / 2
    min_lat = STUDY_SITE_LAT - height_in_degrees / 2
    max_lat = STUDY_SITE_LAT + height_in_degrees / 2
    ax.set_extent([min_lon, max_lon, min_lat, max_lat])

def plot_study_site():
    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent([STUDY_SITE_LON - 5, STUDY_SITE_LON + 5, STUDY_SITE_LAT - 5, STUDY_SITE_LAT + 5])
    
    compass_rose_image = mpimg.imread(COMPASS_ROSE_PATH)
    x0, x1, y0, y1 = ax.get_extent()
    compass_width = (x1 - x0) * 0.1
    compass_height = (y1 - y0) * 0.1
    compass_x = x1 - compass_width * 0.75
    compass_y = y1 - compass_height * 0.75
    ax.imshow(compass_rose_image, extent=[compass_x - compass_width / 2, compass_x + compass_width / 2, compass_y - compass_height / 2, compass_y + compass_height / 2], transform=ccrs.PlateCarree(), zorder=10)
    
    add_scale_bar(ax, 100, location=(0.85, 0.05), color='black', fontsize=6)  # Placing the bar at 5% from the left and bottom of the map

    feature_types = {
        'coastline': 'none',
        'land': '#c8c365',  # Land color
        'geography_marine_polys': '#a6cee3',  # Light blue for marine areas
        'geography_regions_polys': '#bdbdbd'  # Grey for geographic regions
    }


    # Create custom colormap
    colors = ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c']
    levels = [0, 200, 1000, 2000, 3000, 4000, 5000, 6000]
    cmap = LinearSegmentedColormap.from_list('bathymetry', colors, N=len(levels))
    norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

    # Add color bar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])  # This is necessary because our data is not on a regular grid.
    cb = plt.colorbar(sm, ax=ax, boundaries=levels, ticks=levels)
    cb.set_label('Depth (m)')

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
    bathymetry_data = [
        ('ne_10m_bathymetry_L_0', '#f7fbff', '0m'),
        ('ne_10m_bathymetry_K_200', '#deebf7', '200m'),
        ('ne_10m_bathymetry_J_1000', '#c6dbef', '1000m'),
        ('ne_10m_bathymetry_I_2000', '#9ecae1', '2000m'),
        ('ne_10m_bathymetry_H_3000', '#6baed6', '3000m'),
        ('ne_10m_bathymetry_G_4000', '#4292c6', '4000m'),
        ('ne_10m_bathymetry_F_5000', '#2171b5', '5000m'),
        ('ne_10m_bathymetry_E_6000', '#08519c', '6000m')
    ]

    # Load bathymetry files
    for file_name, color, label in bathymetry_data:
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
    plt.legend(loc='upper left', fontsize=8)
    plt.title("R/V Cape Fear, May 03-05 2023, Wilmington, NC")

    gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.savefig(SAVE_PATH, dpi=500, bbox_inches='tight')
    print(f"Map of study site plotted and saved to {SAVE_PATH}.")

if __name__ == "__main__":
    plot_study_site()


