import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import cmocean
import cartopy.crs as ccrs
import cartopy.feature as cfeat
from matplotlib.ticker import FuncFormatter
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', 'visualization', 'maps', 'masonboro')
OUTPUT_FILE = 'sat_chlor_comparison.png'
OUTPUT_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

S3A_FILE_PATH = os.path.join(DATA_DIR, 'sat_default', 's3a', 'l2-l3', 'daily', '300m-chlor_a', 'mean', 'S3A_OLCI_EFRNT.2023050720230507.DLY.chlor_a.map.nc')
S3B_FILE_PATH = os.path.join(DATA_DIR, 'sat_default', 's3b', 'l2-l3', 'daily', '300m-chlor_a', 'mean', 'S3B_OLCI_EFRNT.2023050620230506.DLY.chlor_a.map.nc')

def load_chlor_a_data(file_path):
    # Load chlorophyll-a data from a given NetCDF file.
    with Dataset(file_path, 'r') as nc:
        group = nc.groups['Mapped_Data_and_Params']  # Access the group first
        chlor_a_mean = group.variables['chlor_a-mean'][:]  # Then access the variable within the group
        
        # Check for the _FillValue attribute and handle it if present
        if '_FillValue' in group.variables['chlor_a-mean'].ncattrs():
            fill_value = group.variables['chlor_a-mean']._FillValue  # Get the fill value from the variable
            chlor_a_mean[chlor_a_mean == fill_value] = np.nan  # Replace fill values with NaN
        else:
            chlor_a_mean = np.where(chlor_a_mean.mask, np.nan, chlor_a_mean)  # Use the mask to replace fill values with NaN, if _FillValue is not available
        
        return np.ma.array(chlor_a_mean, mask=np.isnan(chlor_a_mean))  # Return as masked array for NaNs

def calculate_difference(data1, data2):
    # Calculate the day-to-day difference between two datasets.
    return data2 - data1

def check_compatibility(data1, data2):
    # Check if the two datasets have the same shape and are thus compatible.
    if data1.shape != data2.shape:
        raise ValueError("Datasets are not compatible: shapes do not match.")
    
def longitude_formatter(lon):
    # Format longitude labels
    if lon < 0:
        return f"{abs(lon)}°W"
    else:
        return f"{lon}°E"

def latitude_formatter(lat):
    # Format latitude labels
    if lat < 0:
        return f"{abs(lat)}°S"
    else:
        return f"{lat}°N"


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # Define geographical bounds
    lon_west, lon_east, lat_south, lat_north = -77.85, -77.70, 34.10, 34.25


    # Load the chlorophyll-a data
    s3a_chlor_a = load_chlor_a_data(S3A_FILE_PATH)
    s3b_chlor_a = load_chlor_a_data(S3B_FILE_PATH)
        
    # Check if the datasets are compatible (i.e., have the same shape)
    try:
        check_compatibility(s3a_chlor_a, s3b_chlor_a)
    except ValueError as e:
        print(e)
        return
    
     # Calculate the difference between the two satellite datasets
    difference = calculate_difference(s3a_chlor_a, s3b_chlor_a)
    
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent([lon_west, lon_east, lat_south, lat_north], crs=ccrs.PlateCarree())

    # Set the figure and axes background color
    fig.patch.set_facecolor('#FAFAFA')
    ax.patch.set_facecolor('#FAFAFA')  # Sets the plot background color

    # Adding geographical features with specified facecolor for land and ocean
    feature = cfeat.GSHHSFeature(scale='full', levels=[1], facecolor='gray', edgecolor='black')
    ax.add_feature(feature)

    # Ensure NaN values or masked areas in 'difference' are handled to match the background
    img = ax.imshow(difference, cmap=cmocean.cm.balance_r, vmin=-np.nanmax(np.abs(difference)), vmax=np.nanmax(np.abs(difference)),
                extent=[lon_west, lon_east, lat_south, lat_north], transform=ccrs.PlateCarree(), origin='upper')

    # Adding colorbar with label
    cbar = plt.colorbar(img, ax=ax, shrink=0.7)
    cbar.set_label('Chlorophyll-a Diff (µg/L)', fontsize=12)
    
    # Setting x and y labels
    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    
    # Formatting and setting the axis labels and ticks
    ax.set_xticks(np.linspace(lon_west, lon_east, 4), crs=ccrs.PlateCarree())
    ax.set_yticks(np.linspace(lat_south, lat_north, 4), crs=ccrs.PlateCarree())
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: longitude_formatter(x)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: latitude_formatter(y)))
    
    plt.title('Day-to-Day Chlorophyll-a Change (May 6 - May 7)', fontsize=14)
    plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    main()