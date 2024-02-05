import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import cmocean
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from my_hdf_cdf_utilities import *
from my_general_utilities import *

# Paths to the files
acrobat_fname = '/Users/mitchtork/HawkEye_Eval/data/acrobat/050523/transects/processed_transects/processed_dataset.xlsx'
output_acrobat_fname = '/Users/mitchtork/HawkEye_Eval/data/acrobat/050523/transects/processed_transects/satsitu.xlsx'
 
# Satellite data files
hawk_fname = '/Users/mitchtork/HawkEye_Eval/data/satellite_matchups/sensors/hawkeye/l2-l3/daily/chlor_a/mean/SEAHAWK1_HAWKEYE.2023050720230507.chlor_a-mean.smi.nc'
modisa_fname = '/Users/mitchtork/HawkEye_Eval/data/satellite_matchups/sensors/modisa/l2-l3/daily/chlor_a/mean/AQUA_MODIS.2023050720230507.chlor_a-mean.smi.nc'
S3A_fname = '/Users/mitchtork/HawkEye_Eval/data/satellite_matchups/sensors/s3a/l2-l3/daily/chlor_a/mean/S3A_OLCI_EFRNT.2023050720230507.chlor_a-mean.smi.nc'
S3B_fname = '/Users/mitchtork/HawkEye_Eval/data/satellite_matchups/sensors/s3b/l2-l3/daily/chlor_a/mean/S3B_OLCI_EFR.2023050620230506.chlor_a-mean.smi.nc'

prodname = 'chlor_a'
fill_value = -32767.0

# Read in the Excel file of Acrobat data
df = pd.read_excel(acrobat_fname)

# Extract in-situ chlorophyll-a values
in_situ_chlor_a_values = df['chlor_a'].values  # Ensure column name matches

# Read satellite data into numpy arrays
hawk_chl_array = read_hdf_prod(hawk_fname, prodname)
modisa_chl_array = read_hdf_prod(modisa_fname, prodname)
S3A_chl_array = read_hdf_prod(S3A_fname, prodname)
S3B_chl_array = read_hdf_prod(S3B_fname, prodname)

# Replace fill values with NaN
for chl_array in [hawk_chl_array, modisa_chl_array, S3A_chl_array, S3B_chl_array]:
    bad_loc = np.where(chl_array == fill_value)
    chl_array[bad_loc] = np.nan

# Common geographic bounds for all satellite data
bounds = {'north': 34.25, 'south': 34.10, 'east': -77.7, 'west': -77.85}

# Process each record
for i, row in df.iterrows():
    lat = row['lat']
    lon = row['lon']

    def calculate_indices(lat, lon, bounds, array_shape):
        lat_res = (bounds['north'] - bounds['south']) / array_shape[0]
        lon_res = (bounds['east'] - bounds['west']) / array_shape[1]
        irow = int((bounds['north'] - lat) / lat_res)
        icol = int((lon - bounds['west']) / lon_res)
        return irow, icol

    irow_hawk, icol_hawk = calculate_indices(lat, lon, bounds, hawk_chl_array.shape)
    irow_modisa, icol_modisa = calculate_indices(lat, lon, bounds, modisa_chl_array.shape)
    irow_S3A, icol_S3A = calculate_indices(lat, lon, bounds, S3A_chl_array.shape)
    irow_S3B, icol_S3B = calculate_indices(lat, lon, bounds, S3B_chl_array.shape)

    for irow, icol, array, column_name in [
        (irow_hawk, icol_hawk, hawk_chl_array, 'Hawkeye Chl'),
        (irow_modisa, icol_modisa, modisa_chl_array, 'Modisa Chl'),
        (irow_S3A, icol_S3A, S3A_chl_array, 'S3A Chl'),
        (irow_S3B, icol_S3B, S3B_chl_array, 'S3B Chl')
    ]:
        if 0 <= irow < array.shape[0] and 0 <= icol < array.shape[1]:
            df.at[i, column_name] = array[irow, icol]

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
