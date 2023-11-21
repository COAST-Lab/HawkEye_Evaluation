# Script Title: Wrightsville Beach Study Site Map Visualization
# Author: Mitch Torkelson
# Date: Ausgust 2023

# Description:
# This script is designed to generate a visual representation of a study site, specifically for 
# R/V Cape Fear cruises. It showcases the study location with various cartographic 
# enhancements, such as a compass rose, scale bar, and grid lines. The map uses 
# OpenStreetMap as a basemap and highlights the study site with a red marker. The final 
# visualization is saved as a PNG image to a designated folder.

# -----------------
# IMPORTS
# -----------------
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.image as mpimg
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx

# -----------------
# CONSTANTS
# -----------------
STUDY_SITE_LON = -77.696587
STUDY_SITE_LAT = 34.193111
COMPASS_ROSE_PATH = '/Users/macbook/thesis_materials/python/helper_images/compass_rose.png'
SAVE_PATH = "/Users/macbook/thesis_materials/visualization/maps/study_site_map.png"


# -----------------
# HELPER FUNCTIONS
# -----------------
def draw_scale_bar(ax, location, length_km, major_ticks=None, minor_ticks=None, color='black'):
    if major_ticks is None:
        major_ticks = [0, length_km]
    if minor_ticks is None:
        minor_ticks = []

    # Convert location to a shapely Point
    lat, lon = location
    length_deg = length_km / 111  # Conversion from km to degrees
    
    # Major ticks
    for tick in major_ticks:
        tick_lon = lon + (tick / 111)
        ax.plot([tick_lon, tick_lon], [lat, lat - 0.25], color=color, linewidth=0.5, transform=ccrs.PlateCarree())
        if tick == length_km:  # Special label for the last tick
            ax.text(tick_lon, lat - 0.3, f"{tick} km", va='top', ha='center', fontsize=5, transform=ccrs.PlateCarree())
        else:
            ax.text(tick_lon, lat - 0.3, f"{tick}", va='top', ha='center', fontsize=5, transform=ccrs.PlateCarree())
    
    # Minor ticks
    for tick in minor_ticks:
        tick_lon = lon + (tick / 111)
        ax.plot([tick_lon, tick_lon], [lat, lat - 0.15], color=color, linewidth=0.5, transform=ccrs.PlateCarree())
    
    # Draw the scale bar
    ax.plot([lon, lon + length_deg], [lat, lat], color=color, linewidth=0.5, transform=ccrs.PlateCarree())

def set_map_extent(ax, width_in_degrees, height_in_degrees):
    min_lon = STUDY_SITE_LON - width_in_degrees/2
    max_lon = STUDY_SITE_LON + width_in_degrees/2
    min_lat = STUDY_SITE_LAT - height_in_degrees/2
    max_lat = STUDY_SITE_LAT + height_in_degrees/2
    ax.set_extent([min_lon, max_lon, min_lat, max_lat])
    return ax

def plot_study_site():
    width_in_degrees = 10
    height_in_degrees = 10

    # Create a point for the study site
    study_site = gpd.GeoDataFrame([1], geometry=[Point(STUDY_SITE_LON, STUDY_SITE_LAT)], crs="EPSG:4326")

    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': ccrs.PlateCarree()})
    ax = set_map_extent(ax, width_in_degrees, height_in_degrees)
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.COASTLINE, linewidth=0.2)
    ax.add_feature(cfeature.STATES, linewidth=0.2)
    ax.add_feature(cfeature.BORDERS, linewidth=0.2)
    plt.plot(STUDY_SITE_LON, STUDY_SITE_LAT, 'ro', transform=ccrs.PlateCarree(), label="R/V Cape Fear cruises")

    plt.legend(loc='lower right')

    # Grid lines and labels for lat/lon ticks
    xticks = [-84, -82, -80, -78, -76, -74, -72]
    yticks = [30, 32, 34, 36, 38, 40]
    ax.set_xticks(xticks, crs=ccrs.PlateCarree())
    ax.set_yticks(yticks, crs=ccrs.PlateCarree())
    ax.set_xticklabels([f'{abs(x)}° W' for x in xticks])
    ax.set_yticklabels([f'{y}° N' for y in yticks])
    
    # Only use this to set up grid lines
    grid_lines = ax.gridlines(xlocs=xticks, ylocs=yticks, draw_labels=False, zorder=1, linestyle='--', linewidth=0.5)
    grid_lines.xlines = True
    grid_lines.ylines = True
    plt.grid(which='both', linestyle='--', linewidth=0.5, zorder=1)

    # Add a title for the study site map
    plt.title("RV Cape Fear, May 03-05 2023, Wilmington, NC")

    # Add a compass rose to the map in the lower left corner
    compass_rose_image = mpimg.imread(COMPASS_ROSE_PATH)
    compass_position = (-74.5, 37)
    compass_size = 1.5
    ax.imshow(compass_rose_image, extent=[compass_position[0], compass_position[0] + compass_size, compass_position[1], compass_position[1] + compass_size], transform=ccrs.PlateCarree(), zorder=10)

    # Add a scale bar to the map below the compass rose
    scale_bar_location = (compass_position[1] - 0.1, compass_position[0] + 0.3)
    draw_scale_bar(ax, scale_bar_location, 100, major_ticks=[0, 100], minor_ticks=[50])

    # Add a basemap to the map
    ctx.add_basemap(ax, crs=ccrs.PlateCarree(), source=ctx.providers.OpenStreetMap.Mapnik)

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    plt.savefig(SAVE_PATH, dpi=300, bbox_inches='tight')

    plt.show()

    print(f"Map of study site plotted and saved to {SAVE_PATH}.")

# -----------------
# SCRIPT EXECUTION
# -----------------
if __name__ == "__main__":
    plot_study_site()