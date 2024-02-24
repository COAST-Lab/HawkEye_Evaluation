import numpy as np
import pandas as pd
from netCDF4 import Dataset
from my_hdf_cdf_utilities import read_hdf_prod
from my_general_utilities import *

# Function to calculate indices based on fixed geographic bounds
def calculate_indices(lat, lon, array_shape):
    # Fixed geographic bounds
    north_bound = 34.25
    south_bound = 34.10
    east_bound = -77.70
    west_bound = -77.85

    # Calculate the latitude and longitude resolutions
    lat_res = (north_bound - south_bound) / array_shape[0]
    lon_res = (east_bound - west_bound) / array_shape[1]

    # Calculate the row and column indices
    irow = int((north_bound - lat) / lat_res)
    icol = int((lon - west_bound) / lon_res)

    return irow, icol

# Paths to the in situ data
acrobat_fname = '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/processed_dataset.xlsx'
output_acrobat_fname = '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/satsitu.xlsx'

# Satellite data files
satellite_files = {
    'hawkeye': '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/locations/masonboro/hawkeye/daily/chlor_a/mean/SEAHAWK1_HAWKEYE.2023050720230507.chlor_a-mean.smi.nc',
    'modisa': '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/locations/masonboro/modisa/daily/chlor_a/mean/AQUA_MODIS.2023050720230507.chlor_a-mean.smi.nc',
    's3a': '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/locations/masonboro/s3a/daily/chlor_a/mean/S3A_OLCI_EFRNT.2023050720230507.chlor_a-mean.smi.nc',
    's3b': '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/locations/masonboro/s3b/daily/chlor_a/mean/S3B_OLCI_EFR.2023050620230506.chlor_a-mean.smi.nc'
}

# Read in the Excel file of Acrobat data
df = pd.read_excel(acrobat_fname)

# Read satellite data into numpy arrays
satellite_chl_arrays = {}
for sensor_name, file_path in satellite_files.items():
    chl_array = read_hdf_prod(file_path, 'chlor_a')
    satellite_chl_arrays[sensor_name] = chl_array
    print(f"{sensor_name} dimensions: {chl_array.shape} (y, x)")

# Replace fill values with NaN
fill_value = -32767.0
for chl_array in satellite_chl_arrays.values():
    chl_array[chl_array == fill_value] = np.nan

# Process each record for matching satellite data
for i, row in df.iterrows():
    lat = row['lat']
    lon = row['lon']

    for sensor_name, chl_array in satellite_chl_arrays.items():
        irow, icol = calculate_indices(lat, lon, chl_array.shape)
        # Ensure indices are within the bounds of the chlorophyll data array
        if 0 <= irow < chl_array.shape[0] and 0 <= icol < chl_array.shape[1]:
            df.at[i, sensor_name + '_chl'] = chl_array[irow, icol]
        else:
            # Handle cases where calculated indices are outside the array bounds
            df.at[i, sensor_name + '_chl'] = np.nan

# Write the updated DataFrame to a new Excel file
df.to_excel(output_acrobat_fname, index=False)

print("Satellite data matching completed.")
