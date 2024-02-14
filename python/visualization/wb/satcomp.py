import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import cmocean
import cartopy.crs as ccrs
import cartopy.feature as cfeat
from matplotlib.ticker import FuncFormatter
import os

def load_chlor_a_data(file_path):
    # Load chlorophyll-a data from a given NetCDF file.
    with Dataset(file_path, 'r') as nc:
        chlor_a = nc.variables['chlor_a'][:]
        chlor_a[chlor_a == nc.variables['chlor_a']._FillValue] = np.nan  # Handle fill values
        return np.ma.array(chlor_a, mask=np.isnan(chlor_a))  # Return as masked array for NaNs

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

    output_dir = '/Users/mitchtork/HawkEye_Evaluation/visualization/maps/masonboro'
    output_file = 'sat_chlor_comparison.png'
    output_path = os.path.join(output_dir, output_file)
    
    # Check if the output directory exists, and create it if it doesn't
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Define geographical bounds
    lon_west, lon_east, lat_south, lat_north = -77.85, -77.70, 34.10, 34.25

    # File paths to the chlorophyll-a data from Sentinel-3A and Sentinel-3B
    s3a_file_path = '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/locations/masonboro/s3a/daily/chlor_a/mean/S3A_OLCI_EFRNT.2023050720230507.chlor_a-mean.smi.nc'
    s3b_file_path = '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/locations/masonboro/s3b/daily/chlor_a/mean/S3B_OLCI_EFR.2023050620230506.chlor_a-mean.smi.nc'
    
    # Load the chlorophyll-a data
    s3a_chlor_a = load_chlor_a_data(s3a_file_path)
    s3b_chlor_a = load_chlor_a_data(s3b_file_path)

        
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
    
    # Adding geographical features
    feature = cfeat.GSHHSFeature(scale='full', levels=[1], facecolor='gray', edgecolor='black')
    ax.add_feature(feature)
    
    # Plotting the data
    img = ax.imshow(difference, cmap=cmocean.cm.balance_r, vmin=-np.nanmax(np.abs(difference)), vmax=np.nanmax(np.abs(difference)),
                    extent=[lon_west, lon_east, lat_south, lat_north], transform=ccrs.PlateCarree(), origin='upper')
    
    # Adding colorbar with label
    cbar = plt.colorbar(img, ax=ax, shrink=0.7)
    cbar.set_label('Chlorophyll-a Diff (mg m^-3)', fontsize=12)
    
    # Setting x and y labels
    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    
    # Formatting and setting the axis labels and ticks
    ax.set_xticks(np.linspace(lon_west, lon_east, 5), crs=ccrs.PlateCarree())
    ax.set_yticks(np.linspace(lat_south, lat_north, 5), crs=ccrs.PlateCarree())
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: longitude_formatter(x)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: latitude_formatter(y)))
    
    plt.title('Day-to-Day Chlorophyll-a Change (May 6 - May 7)', fontsize=14)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    main()