import numpy as np
import pandas as pd
from netCDF4 import Dataset
import os

# Dynamically set the base directory to the script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define paths for Acrobat and satellite data relative to BASE_DIR
ACROBAT_DIR = os.path.join(BASE_DIR, 'data', 'acrobat', '050523', 'transects', 'processed_transects')
SATELLITE_DIR = os.path.join(BASE_DIR, 'data', 'satellite_matchups')

acrobat_fname = os.path.join(ACROBAT_DIR, 'processed_dataset.csv')
output_acrobat_fname = os.path.join(ACROBAT_DIR, 'satsitu_l2.csv')

# Satellite data files with relative paths
satellite_files = {
    'hawkeye': os.path.join(SATELLITE_DIR, 'sensors', 'hawkeye', 'l1a-l2', 'SEAHAWK1_HAWKEYE.20230507T150955.L2.OC.nc'),
    'modisa': os.path.join(SATELLITE_DIR, 'sensors', 'modisa', 'l1a-l2', 'AQUA_MODIS.20230507T184500.L2.OC.nc'),
    's3b': os.path.join(SATELLITE_DIR, 'sensors', 's3b', 'l1a-l2', 'S3B_OLCI_EFR.20230506T152110.L2.OC.nc'),
    's3a': os.path.join(SATELLITE_DIR, 'sensors', 's3a', 'l1a-l2', 'S3A_OLCI_EFR.20230507T153409.L2.OC.nc'),
    'oli8': os.path.join(SATELLITE_DIR, 'sensors', 'landsat', 'l1a-l2', 'LANDSAT8_OLI.20230503T000000.L2.OC.nc')
}

# New function to read a product from netCDF4 file, considering group structures
def read_product_netCDF4(file_path, product_name, group_name):
    try:
        with Dataset(file_path, 'r') as nc:
            group = nc.groups[group_name]
            product_data = group.variables[product_name][:]
            return product_data
    except KeyError as e:
        print(f"KeyError - the variable '{product_name}' in group '{group_name}' was not found in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"An error occurred while reading '{product_name}' from {file_path}: {e}")
        return None

# Function to calculate indices based on fixed geographic bounds remains unchanged
def calculate_indices(lat, lon, array_shape):
    north_bound = 34.25
    south_bound = 34.10
    east_bound = -77.70
    west_bound = -77.85

    lat_res = (north_bound - south_bound) / array_shape[0]
    lon_res = (east_bound - west_bound) / array_shape[1]

    irow = int((north_bound - lat) / lat_res)
    icol = int((lon - west_bound) / lon_res)

    return irow, icol

# Read in the Excel file of Acrobat data
df = pd.read_csv(acrobat_fname)

# Read satellite data into numpy arrays, now using the updated function
satellite_chl_arrays = {}
for sensor_name, file_path in satellite_files.items():
    # Adjust the product name and group name based on your netCDF structure
    chl_array = read_product_netCDF4(file_path, 'chlor_a', 'geophysical_data')
    if chl_array is None:
        print(f"Failed to read chlor_a-mean data from {sensor_name}")
    else:
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
            # Store the calculated row and column indices
            df.at[i, sensor_name + '_irow'] = irow
            df.at[i, sensor_name + '_icol'] = icol
        else:
            # Handle cases where calculated indices are outside the array bounds
            df.at[i, sensor_name + '_chl'] = np.nan
            # Set indices to NaN or another placeholder if out-of-bounds
            df.at[i, sensor_name + '_irow'] = np.nan
            df.at[i, sensor_name + '_icol'] = np.nan

# Write the updated DataFrame to a new Excel file
df.to_csv(output_acrobat_fname, index=False)

print("Satellite data matching and index recording completed.")

