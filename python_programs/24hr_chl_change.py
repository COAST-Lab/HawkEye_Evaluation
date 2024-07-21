import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import cmocean
import cartopy.crs as ccrs
import cartopy.feature as cfeat
import matplotlib.ticker as mticker
import os

# Define font size variables
title_fontsize = 24
label_fontsize = 20
tick_label_fontsize = 18
colorbar_label_fontsize = 18
colorbar_tick_fontsize = 18

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', 'visualization', 'maps')
OUTPUT_FILE = 'sat_chlor_comparison.png'
OUTPUT_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

S3A_FILE_PATH = os.path.join(DATA_DIR, 'satellite', 's3a', 'l2-l3', 'daily', '300m-chlor_a', 'mean', 'S3A_OLCI_EFRNT.2023050720230507.DLY.chlor_a.map.nc')
S3B_FILE_PATH = os.path.join(DATA_DIR, 'satellite', 's3b', 'l2-l3', 'daily', '300m-chlor_a', 'mean', 'S3B_OLCI_EFRNT.2023050620230506.DLY.chlor_a.map.nc')

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

def round_ticks(value, pos):
    return f"{value:.2f}"

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # Define geographical bounds
    lon_west, lon_east, lat_south, lat_north = -77.85, -77.70, 34.10, 34.25
    extent = [lon_west, lon_east, lat_south, lat_north]

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
    
    extreme_swing = np.nanmax(np.abs(difference))
    print(f"Most extreme chlorophyll change observed: {extreme_swing:.2f} µg/L")

    # Calculate and print the average day-to-day chlorophyll change
    average_change = np.nanmean(difference)
    print(f"Average day-to-day chlorophyll change: {average_change:.2f} µg/L")

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent(extent, crs=ccrs.PlateCarree())

    # Set the figure and axes background color
    fig.patch.set_facecolor('#FFFFFF')
    ax.patch.set_facecolor('#FFFFFF')  # Sets the plot background color

    # Adding geographical features with specified facecolor for land and ocean
    feature = cfeat.GSHHSFeature(scale='full', levels=[1], facecolor='gray', edgecolor='black')
    ax.add_feature(feature)

    # Ensure NaN values or masked areas in 'difference' are handled to match the background
    img = ax.imshow(difference, cmap=cmocean.cm.balance_r, vmin=-np.nanmax(np.abs(difference)), vmax=np.nanmax(np.abs(difference)),
                    extent=extent, transform=ccrs.PlateCarree(), origin='upper')

    # Adding colorbar with label
    cbar = plt.colorbar(img, ax=ax)
    cbar.set_label('Δ[Chl a] (µg/L)', fontsize=colorbar_label_fontsize)
    cbar.ax.tick_params(labelsize=colorbar_tick_fontsize)

    # Setting x and y labels
    ax.set_xlabel('Longitude', fontsize=label_fontsize)
    ax.set_ylabel('Latitude', fontsize=label_fontsize)
    
    # Formatting and setting the axis labels and ticks
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xlocator = mticker.FixedLocator(np.round(np.arange(lon_west, lon_east, 0.03), 2))
    gl.ylocator = mticker.FixedLocator(np.round(np.arange(lat_south, lat_north, 0.03), 2))
    gl.xlabel_style = {'size': tick_label_fontsize}
    gl.ylabel_style = {'size': tick_label_fontsize}
    gl.xformatter = mticker.FuncFormatter(round_ticks)
    gl.yformatter = mticker.FuncFormatter(round_ticks)
    
    plt.title('24-Hour Δ[Chl a] (µg/L)', fontsize=title_fontsize)
    plt.savefig(OUTPUT_PATH, dpi=500, bbox_inches='tight')

if __name__ == "__main__":
    main()