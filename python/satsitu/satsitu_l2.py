import os
import glob
import numpy as np
import pandas as pd
from netCDF4 import Dataset
from datetime import datetime
import warnings

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', '..', 'data')
ACROBAT_DIR = os.path.join(DATA_DIR, 'acrobat', '050523', 'transects', 'processed_csv')
SATELLITE_DIR = os.path.join(DATA_DIR, 'sat_default')

acrobat_fname = os.path.join(ACROBAT_DIR, 'combined_transects.csv')
output_acrobat_fname = os.path.join(DATA_DIR, 'satsitu', 'satsitu_l2.csv')
OUTPUT_DIR = os.path.dirname(output_acrobat_fname)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

warnings.filterwarnings('ignore', category=UserWarning)


# Define satellite directories
satellite_dirs = {
    'hawkeye': os.path.join(SATELLITE_DIR, 'hawkeye', 'l2'),
    'modisa': os.path.join(SATELLITE_DIR, 'modisa', 'l2'),
    's3b': os.path.join(SATELLITE_DIR, 's3b', 'l2'),
    's3a': os.path.join(SATELLITE_DIR, 's3a', 'l2'),
    'landsat': os.path.join(SATELLITE_DIR, 'landsat', 'l2')
}

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

# Read in the csv file of Acrobat data
df = pd.read_csv(acrobat_fname)

satellite_chl_arrays = {}
for _, dir_path in satellite_dirs.items():
    for file_path in glob.glob(os.path.join(dir_path, '*.nc')):
        chl_array = read_product_netCDF4(file_path, 'chlor_a', 'geophysical_data')
        if chl_array is not None:
            file_name = os.path.basename(file_path)
            date_str = file_name.split('.')[1]
            date = datetime.strptime(date_str, "%Y%m%dT%H%M%S").date()
            unique_identifier = os.path.basename(file_path).replace('.nc', '')
            satellite_chl_arrays[unique_identifier] = {'chl_array': chl_array, 'date': date}

fill_value = -32767.0
for sensor_data in satellite_chl_arrays.values():
    chl_array = sensor_data['chl_array']
    chl_array[chl_array == fill_value] = np.nan

for i, row in df.iterrows():
    lat = row['lat']
    lon = row['lon']
    for unique_identifier, sensor_data in satellite_chl_arrays.items():
        chl_array = sensor_data['chl_array']
        date = sensor_data['date']
        irow, icol = calculate_indices(lat, lon, chl_array.shape)
        if 0 <= irow < chl_array.shape[0] and 0 <= icol < chl_array.shape[1]:
            df.at[i, f"{unique_identifier}_irow"] = irow
            df.at[i, f"{unique_identifier}_icol"] = icol
            df.at[i, f"{unique_identifier}_chl"] = chl_array[irow, icol]
        else:
            df.at[i, f"{unique_identifier}_chl"] = np.nan
            df.at[i, f"{unique_identifier}_irow"] = np.nan
            df.at[i, f"{unique_identifier}_icol"] = np.nan

df.to_csv(output_acrobat_fname, index=False)
print(f"Output CSV saved to {output_acrobat_fname}. Satellite data matching and index recording completed.")
