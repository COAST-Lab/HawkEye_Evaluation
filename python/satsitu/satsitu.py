import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from netCDF4 import Dataset
from scipy.stats import pearsonr
from my_hdf_cdf_utilities import *
from my_general_utilities import *

# Function to read geographic information
def read_geo_info(nc_file):
    with Dataset(nc_file, 'r') as nc:
        lat = nc.variables['lat'][:]
        lon = nc.variables['lon'][:]
    return np.min(lat), np.max(lat), np.min(lon), np.max(lon)

# Function to calculate indices based on geographic bounds
def calculate_indices(lat, lon, bounds, array_shape):
    lat_range = bounds['north'] - bounds['south']
    lon_range = bounds['east'] - bounds['west']

    # Check for zero division
    if lat_range == 0 or lon_range == 0:
        raise ValueError("Invalid bounds: Latitude or Longitude range cannot be zero")

    lat_res = lat_range / array_shape[0]
    lon_res = lon_range / array_shape[1]

    irow = int((bounds['north'] - lat) / lat_res)
    icol = int((lon - bounds['west']) / lon_res)
    return irow, icol

# Paths to the files
acrobat_fname = '/Users/mitchtork/HawkEye_Eval/data/acrobat/050523/transects/processed_transects/processed_dataset.xlsx'
output_acrobat_fname = '/Users/mitchtork/HawkEye_Eval/data/acrobat/050523/transects/processed_transects/satsitu.xlsx'

# Satellite data files
satellite_files = {
    'HawkEye': '/Users/mitchtork/HawkEye_Eval/data/satellite_matchups/sensors/hawkeye/l2-l3/daily/chlor_a/mean/SEAHAWK1_HAWKEYE.2023050720230507.chlor_a-mean.smi.nc',
    'MODISA': '/Users/mitchtork/HawkEye_Eval/data/satellite_matchups/sensors/modisa/l2-l3/daily/chlor_a/mean/AQUA_MODIS.2023050720230507.chlor_a-mean.smi.nc',
    'Sentinel3A': '/Users/mitchtork/HawkEye_Eval/data/satellite_matchups/sensors/s3a/l2-l3/daily/chlor_a/mean/S3A_OLCI_EFRNT.2023050720230507.chlor_a-mean.smi.nc',
    'Sentinel3B': '/Users/mitchtork/HawkEye_Eval/data/satellite_matchups/sensors/s3b/l2-l3/daily/chlor_a/mean/S3B_OLCI_EFR.2023050620230506.chlor_a-mean.smi.nc'
}

# Read in the Excel file of Acrobat data
df = pd.read_excel(acrobat_fname)

# Read satellite data into numpy arrays and calculate dynamic bounds
satellite_chl_arrays = {}
bounds = {}
for sensor_name, file_path in satellite_files.items():
    chl_array = read_hdf_prod(file_path, 'chlor_a')
    south, north, west, east = read_geo_info(file_path)
    bounds[sensor_name] = {'north': north, 'south': south, 'east': east, 'west': west}
    satellite_chl_arrays[sensor_name] = chl_array

# Replace fill values with NaN
fill_value = -32767.0
for chl_array in satellite_chl_arrays.values():
    chl_array[chl_array == fill_value] = np.nan

# Process each record for matching satellite data
for i, row in df.iterrows():
    lat = row['lat']
    lon = row['lon']

    for sensor_name, chl_array in satellite_chl_arrays.items():
        irow, icol = calculate_indices(lat, lon, bounds[sensor_name], chl_array.shape)
        if 0 <= irow < chl_array.shape[0] and 0 <= icol < chl_array.shape[1]:
            df.at[i, sensor_name + ' Chl'] = chl_array[irow, icol]

# Statistical Analysis
in_situ_chlor_a_values = df['chlor_a'].values
for sensor_name in satellite_files.keys():
    satellite_data = df[sensor_name + ' Chl'].values
    valid_mask = ~np.isnan(satellite_data) & ~np.isnan(in_situ_chlor_a_values)
    correlation, _ = pearsonr(satellite_data[valid_mask], in_situ_chlor_a_values[valid_mask])
    mean_abs_diff = np.mean(np.abs(satellite_data[valid_mask] - in_situ_chlor_a_values[valid_mask]))
    print(f"Correlation Coefficient ({sensor_name} vs In-Situ): {correlation}")
    print(f"Mean Absolute Difference ({sensor_name} vs In-Situ): {mean_abs_diff}")

# Write the updated DataFrame to a new Excel file
df.to_excel(output_acrobat_fname, index=False)

# Function to plot comparison
def plot_comparison(satellite_data, in_situ_data, title, bounds, latitudes, longitudes, save_path, sensor_name):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), subplot_kw={'projection': ccrs.PlateCarree()})

    # Add coastlines using Cartopy
    feature = cfeature.GSHHSFeature(scale='full', levels=[1], facecolor='gray', edgecolor='black')
    ax1.add_feature(feature)
    ax2.add_feature(feature)

    im = ax1.imshow(satellite_data, extent=(bounds['west'], bounds['east'], bounds['south'], bounds['north']), interpolation='none', cmap='viridis', transform=ccrs.PlateCarree())
    fig.colorbar(im, ax=ax1, label='Satellite Chlorophyll concentration')
    ax1.set_title(title + ' - Satellite')

    sc = ax2.scatter(longitudes, latitudes, c=in_situ_data, cmap='viridis', edgecolors='none', s=30, alpha=0.7, transform=ccrs.PlateCarree())
    fig.colorbar(sc, ax=ax2, label='In-Situ Chlorophyll concentration')
    ax2.set_title(title + ' - In-Situ')

    file_name = os.path.join(save_path, sensor_name + '_comparison.png')
    plt.savefig(file_name)
    plt.close()

# Extract latitudes and longitudes from the DataFrame
latitudes = df['lat'].values
longitudes = df['lon'].values

# Paths for saving heat maps
save_path = '/Users/mitchtork/HawkEye_Eval/visualization/maps/heat_maps'

# Generate comparison plots for each satellite dataset
plot_comparison(hawk_chl_array, in_situ_chlor_a_values, 'HawkEye Chlorophyll Comparison', bounds, latitudes, longitudes, save_path, 'HawkEye')
plot_comparison(modisa_chl_array, in_situ_chlor_a_values, 'MODISA Chlorophyll Comparison', bounds, latitudes, longitudes, save_path, 'MODISA')
plot_comparison(S3A_chl_array, in_situ_chlor_a_values, 'Sentinel-3A Chlorophyll Comparison', bounds, latitudes, longitudes, save_path, 'Sentinel3A')
plot_comparison(S3B_chl_array, in_situ_chlor_a_values, 'Sentinel-3B Chlorophyll Comparison', bounds, latitudes, longitudes, save_path, 'Sentinel3B')
