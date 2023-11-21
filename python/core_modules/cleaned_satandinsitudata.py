import numpy as np
from my_hdf_cdf_utilities import *

# Define paths
path_acrobat_data = '/Users/macbook/data/acrobat/05052023/wing_angle2_dataonly.txt'
path_output_acrobat = '/Users/macbook/data/acrobat/05052023/cleaned_satellite_acrobat_chlor'
path_satellite_matchups = '/Users/macbook/data/satellite_matchups/smaller_area/not_straight_map'

satellite_files = {
    'hawk': f'{path_satellite_matchups}/hawkeye/l2-l3/daily/chlor_a/mean/SEAHAWK1_HAWKEYE.2023050620230506.chlor_a-mean.smi.nc',
    'modisa': f'{path_satellite_matchups}/modisa/l2-l3/daily/chlor_a/mean/AQUA_MODIS.2023050720230507.chlor_a-mean.smi.nc',
    'S3A': f'{path_satellite_matchups}/S3A/l2-l3/daily/chlor_a/mean/S3A_OLCI_EFRNT.2023050720230507.chlor_a-mean.smi.nc',
    'S3B': f'{path_satellite_matchups}/S3B/l2-l3/daily/chlor_a/mean/S3B_OLCI_EFRNT.2023050620230506.chlor_a-mean.smi.nc'
}

fill_value = -32767.0

# Function to read chlorophyll data and replace fill values with NaN
def read_chl_array(filename):
    chl_array = read_hdf_prod(filename, 'chlor_a')
    bad_loc = np.where(chl_array == fill_value)
    chl_array[bad_loc] = np.nan
    return chl_array

# Function to convert lat/lon to row/column
def latlon_to_rowcol(lat, lon, scale):
    irow = int(scale['irow_factor'] - lat * scale['irow_multiplier'])
    icol = int((lon + scale['ilon_add']) * scale['icol_multiplier'])
    return irow, icol

# Reading chlorophyll arrays
chl_arrays = {key: read_chl_array(filename) for key, filename in satellite_files.items()}

# Scaling factors for row/column conversion
scales = {
    'hawk': {'irow_factor': 36.0, 'irow_multiplier': 1781.0 / 4.0, 'ilon_add': 78.5, 'icol_multiplier': 1113.0 / 2.5},
    'modisa': {'irow_factor': 36.0, 'irow_multiplier': 405.0 / 4.0, 'ilon_add': 78.5, 'icol_multiplier': 253.0 / 2.5},
    'S3A': {'irow_factor': 36.0, 'irow_multiplier': 891.0 / 4.0, 'ilon_add': 78.5, 'icol_multiplier': 557.0 / 2.5},
    'S3B': {'irow_factor': 40.0, 'irow_multiplier': 1011.0 / 10.0, 'ilon_add': 80, 'icol_multiplier': 1011.0 / 10.0}
}

with open(path_acrobat_data, 'r') as f1, open(path_output_acrobat, 'w') as f2:
    header_line = f1.readline().strip()
    f2.write(header_line + '\tHawkeye Chl' + '\tModisa Chl' + '\tS3A Chl' + '\tS3B Chl\n')

    for line in f1:
        one_line = line.strip()
        elements = one_line.split('\t')
        lat = float(elements[11])
        lon = float(elements[12])

        satellite_chls = []
        for key, chl_array in chl_arrays.items():
            irow, icol = latlon_to_rowcol(lat, lon, scales[key])
            satellite_chls.append(chl_array[irow, icol])

        f2.write(one_line + '\t' + '\t'.join(map(str, satellite_chls)) + '\n')
