import numpy as np
import pandas as pd
from netCDF4 import Dataset
import os
from my_hdf_cdf_utilities import read_hdf_prod
from my_general_utilities import *

# Function to calculate indices based on fixed geographic bounds
def calculate_indices(lat, lon, north_bound, south_bound, east_bound, west_bound, array_shape):
    lat_res = (north_bound - south_bound) / array_shape[0]
    lon_res = (east_bound - west_bound) / array_shape[1]
    irow = int((north_bound - lat) / lat_res)
    icol = int((lon - west_bound) / lon_res)
    return irow, icol

def indices_to_latlon(irow, icol, north_bound, south_bound, east_bound, west_bound, array_shape):
    lat_res = (north_bound - south_bound) / array_shape[0]
    lon_res = (east_bound - west_bound) / array_shape[1]
    lat = north_bound - (irow * lat_res + lat_res / 2)  # Center of the pixel
    lon = west_bound + (icol * lon_res + lon_res / 2)  # Center of the pixel
    return lat, lon

# Satellite data files
satellite_files = {
    'hawkeye': '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/sensors/hawkeye/l1a-l3/daily/75m-chlor_a/mean/SEAHAWK1_HAWKEYE.2023050720230507.DLY.chlor_a.map.nc',
    'modisa': '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/sensors/modisa/l1a-l3/daily/1000m-chlor_a/mean/AQUA_MODIS.2023050720230507.DLY.chlor_a.map.nc',
    's3b': '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/sensors/s3b/l1a-l3/daily/300m-chlor_a/mean/S3B_OLCI_EFR.2023050620230506.DLY.chlor_a.map.nc',
    's3a': '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/sensors/s3a/l1a-l3/daily/300m-chlor_a/mean/S3A_OLCI_EFR.2023050720230507.DLY.chlor_a.map.nc',
    'oli8': '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/sensors/landsat/l1a-l3/daily/30m-chlor_a/mean/LANDSAT8_OLI.2023050320230503.DLY.chlor_a.map.nc'
}

# Fixed geographic bounds (assuming these are consistent across all sensors)
north_bound = 34.25
south_bound = 34.10
east_bound = -77.70
west_bound = -77.85

# Prepare a DataFrame to hold the consolidated data
columns = ['sensor_name', 'irow', 'icol', 'chlor_a']
consolidated_data = pd.DataFrame(columns=columns)

# Loop through each satellite file
for sensor_name, file_path in satellite_files.items():
    chl_array = read_hdf_prod(file_path, 'chlor_a')
    # Replace fill values with NaN
    fill_value = -32767.0
    chl_array[chl_array == fill_value] = np.nan
    
    # Loop through each pixel in the chlorophyll array
    for irow in range(chl_array.shape[0]):
        for icol in range(chl_array.shape[1]):
            # Convert the irow and icol back to lat/lon to ensure consistency
            lat, lon = indices_to_latlon(irow, icol, north_bound, south_bound, east_bound, west_bound, chl_array.shape)
            chlor_a = chl_array[irow, icol]
            if not np.isnan(chlor_a):  # Only add entries with valid chlorophyll data
                consolidated_data = consolidated_data._append({
                    'sensor_name': sensor_name,
                    'irow': irow,
                    'icol': icol,
                    'lat': lat,
                    'lon': lon,
                    'chlor_a': chlor_a
                }, ignore_index=True)

# Calculate and print the global min/max chlorophyll measurement
global_chl_min = consolidated_data['chlor_a'].min()
global_chl_max = consolidated_data['chlor_a'].max()
print(f"Global minimum chlorophyll measurement: {global_chl_min}")
print(f"Global maximum chlorophyll measurement: {global_chl_max}")

# Path correction for saving the DataFrame to a CSV file
output_dir = '/Users/mitchtork/HawkEye_Evaluation/data/satsitu/sat_chl_array/'
output_file = os.path.join(output_dir, "master_dataset.csv")  # Define the full output filepath

# Check if output directory exists, if not, create it
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
# Save the DataFrame to a CSV file
consolidated_data.to_csv(output_file, index=False)

print("CSV file with unique irow/icol chlorophyll measurements created.")
