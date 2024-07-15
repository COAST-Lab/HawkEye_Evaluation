import os
import glob
import numpy as np
import pandas as pd
from netCDF4 import Dataset
from datetime import datetime
import warnings

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data')
ACROBAT_DIR = os.path.join(DATA_DIR, 'acrobat', 'transects', 'processed')
SATELLITE_DIR = os.path.join(DATA_DIR, 'sat_default', 'all_l2')

acrobat_fname = os.path.join(ACROBAT_DIR, 'processed_dataset.csv')
output_acrobat_fname = os.path.join(DATA_DIR, 'satsitu', 'satsitu_l2_kd490.csv')
OUTPUT_DIR = os.path.dirname(output_acrobat_fname)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

warnings.filterwarnings('ignore', category=UserWarning)

# Define satellite directories
satellite_dirs = {
    'hawkeye': os.path.join(SATELLITE_DIR),
    'modisa': os.path.join(SATELLITE_DIR),
    's3b': os.path.join(SATELLITE_DIR),
    's3a': os.path.join(SATELLITE_DIR),
    'landsat': os.path.join(SATELLITE_DIR)
}

def read_product_netCDF4(file_path, product_name, group_name='geophysical_data'):
    try:
        with Dataset(file_path, 'r') as nc:
            if group_name in nc.groups:
                group = nc.groups[group_name]
                if product_name in group.variables:
                    product_data = group.variables[product_name][:]
                    return product_data
                else:
                    print(f"Variable '{product_name}' not found in group '{group_name}'.")
            else:
                print(f"Group '{group_name}' not found.")
    except Exception as e:
        print(f"An error occurred while reading from {file_path}: {e}")
    return None
    
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

satellite_kd490_arrays = {}
for _, dir_path in satellite_dirs.items():
    for file_path in glob.glob(os.path.join(dir_path, '*.nc')):
        kd490_array = read_product_netCDF4(file_path, 'Kd_490', 'geophysical_data')
        if kd490_array is not None:
            file_name = os.path.basename(file_path)
            date_str = file_name.split('.')[1]
            date = datetime.strptime(date_str, "%Y%m%dT%H%M%S").date()
            unique_identifier = os.path.basename(file_path).replace('.nc', '')
            satellite_kd490_arrays[unique_identifier] = {'kd490_array': kd490_array, 'date': date}

fill_value = -32767.0
for sensor_data in satellite_kd490_arrays.values():
    kd490_array = sensor_data['kd490_array']
    kd490_array[kd490_array == fill_value] = np.nan

for i, row in df.iterrows():
    lat = row['lat']
    lon = row['lon']
    for unique_identifier, sensor_data in satellite_kd490_arrays.items():
        kd490_array = sensor_data['kd490_array']
        date = sensor_data['date']
        irow, icol = calculate_indices(lat, lon, kd490_array.shape)
        if 0 <= irow < kd490_array.shape[0] and 0 <= icol < kd490_array.shape[1]:
            df.at[i, f"{unique_identifier}_irow"] = irow
            df.at[i, f"{unique_identifier}_icol"] = icol
            df.at[i, f"{unique_identifier}_kd490"] = kd490_array[irow, icol]
        else:
            df.at[i, f"{unique_identifier}_kd490"] = np.nan
            df.at[i, f"{unique_identifier}_irow"] = np.nan
            df.at[i, f"{unique_identifier}_icol"] = np.nan

df.to_csv(output_acrobat_fname, index=False)
print(f"Output CSV saved to {output_acrobat_fname}. Satellite data matching and index recording completed.")
