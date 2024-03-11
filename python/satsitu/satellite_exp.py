import numpy as np
import pandas as pd
from netCDF4 import Dataset
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
    'hawkeye': '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/locations/masonboro/hawkeye/daily/chlor_a/mean/SEAHAWK1_HAWKEYE.2023050720230507.chlor_a-mean.smi.nc',
    'modisa': '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/locations/masonboro/modisa/daily/chlor_a/mean/AQUA_MODIS.2023050720230507.chlor_a-mean.smi.nc',
    's3a': '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/locations/masonboro/s3a/daily/chlor_a/mean/S3A_OLCI_EFRNT.2023050720230507.chlor_a-mean.smi.nc',
    's3b': '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/locations/masonboro/s3b/daily/chlor_a/mean/S3B_OLCI_EFR.2023050620230506.chlor_a-mean.smi.nc'
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

# Note: Ensure the indices_to_latlon function converts irow/icol back to geographic coordinates correctly
# This function is not defined here and should be implemented based on your specific needs

# Finally, save the DataFrame to an Excel file
output_excel_file = '/Users/mitchtork/HawkEye_Evaluation/data/satsitu/satellite_chl_arrays/output_file.xlsx'
consolidated_data.to_excel(output_excel_file, index=False)

print("Excel file with unique irow/icol chlorophyll measurements created.")
