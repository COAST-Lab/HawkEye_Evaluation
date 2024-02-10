import numpy as np
import pandas as pd
from netCDF4 import Dataset
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

# Paths to the in situ data
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

# Write the updated DataFrame to a new Excel file
df.to_excel(output_acrobat_fname, index=False)


