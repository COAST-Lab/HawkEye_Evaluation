import xarray as xr
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load the L3 satellite data NetCDF
satellite_data = xr.open_dataset('/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/sensors/hawkeye/020524/l1a-l3/daily/chlor_a/mean/SEAHAWK1_HAWKEYE.2023050720230507.chlor_a-mean.smi.nc')

# Load the in-situ Acrobat data
in_situ_data = pd.read_excel('/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/processed_dataset.xlsx')

gdf = gpd.GeoDataFrame(in_situ_data, geometry=gpd.points_from_xy(in_situ_data['lon'], in_situ_data['lat']))

chlor_a_var_name = 'chlor_a'

# Placeholder list to store satellite chlorophyll-a values corresponding to in-situ measurements
satellite_chl_a_values = []

# Iterate over the in-situ GeoDataFrame
for index, row in gdf.iterrows():
    # Extract the in-situ measurement's location
    lon, lat = row['lon'], row['lat']
    
    # Find the nearest satellite chlorophyll-a value
    nearest_chl_a_value = satellite_data[chlor_a_var_name].sel(lat=lat, lon=lon, method='nearest').values
    satellite_chl_a_values.append(nearest_chl_a_value)

# Add the satellite chlorophyll-a values to the in-situ GeoDataFrame
gdf['satellite_chl_a'] = satellite_chl_a_values

# Optionally, save the combined data to a new file for further analysis or visualization
gdf.to_file("matched_satellite_in_situ_data.geojson", driver='GeoJSON')
