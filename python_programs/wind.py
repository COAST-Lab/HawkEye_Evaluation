import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeat
import cmocean
from scipy.interpolate import griddata
import os
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import pandas as pd

# Define font size variables
title_fontsize = 14
label_fontsize = 12
tick_label_fontsize = 10

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WIND_DIR = os.path.join(SCRIPT_DIR, 'local_processing_resources', 'meteorological', 'wind', 'adaptor.mars.internal-1706121221.9677804-13631-13-0aaf00c1-19ae-407a-a7ee-7520794a10dc.nc')
SAVE_DIR = os.path.join(SCRIPT_DIR, '..', 'visualization', 'meteorological', 'wind')
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

lat_south, lon_west, lat_north, lon_east = 33.80, -78.05, 34.40, -77.45

time_windows = [
    ('2023-05-05T00:00:00', '2023-05-05T23:59:59'),
    ('2023-05-06T00:00:00', '2023-05-06T23:59:59'),
    ('2023-05-07T00:00:00', '2023-05-07T23:59:59')
]

for start, end in time_windows:
    with xr.open_dataset(WIND_DIR) as ncw:
        time_slice = ncw.sel(time=slice(start, end)).mean('time')
        u = time_slice['u10']
        v = time_slice['v10']
        lon = time_slice['longitude']
        lat = time_slice['latitude']

        u_np = u.values
        v_np = v.values
        lon_np = lon.values
        lat_np = lat.values

        wind_speed = np.sqrt(u_np**2 + v_np**2)

        min_wind_speed = wind_speed.min()
        max_wind_speed = wind_speed.max()
        
        print(f"Wind speed from {start} to {end}:")
        print(f"  Minimum average: {min_wind_speed:.2f} m/s")
        print(f"  Maximum average: {max_wind_speed:.2f} m/s")

        lon2D, lat2D = np.meshgrid(lon_np, lat_np)
        lon_flat = lon2D.flatten()
        lat_flat = lat2D.flatten()
        wind_speed_flat = wind_speed.flatten()

        buffer = 0.1
        lon_dense, lat_dense = np.meshgrid(np.linspace(lon_west - buffer, lon_east + buffer, 500),
                                           np.linspace(lat_south - buffer, lat_north + buffer, 500))

        wind_speed_dense = griddata((lon_flat, lat_flat), wind_speed_flat, (lon_dense, lat_dense), method='cubic')

        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.set_extent([lon_west, lon_east, lat_south, lat_north], crs=ccrs.PlateCarree())
        feature = cfeat.GSHHSFeature(scale='full', levels=[1], facecolor='gray', edgecolor='black')
        ax.add_feature(feature)

        speed_plot = ax.pcolormesh(lon_dense, lat_dense, wind_speed_dense, 
                                   transform=ccrs.PlateCarree(), 
                                   cmap=cmocean.cm.haline, 
                                   vmin=min_wind_speed, 
                                   vmax=max_wind_speed)

        ax.quiver(lon_np, lat_np, u_np, v_np, color='black', transform=ccrs.PlateCarree())

        xticks = np.arange(lon_west, lon_east, 0.1)
        yticks = np.arange(lat_south, lat_north, 0.1)
        ax.set_xticks(xticks, crs=ccrs.PlateCarree())
        ax.set_yticks(yticks, crs=ccrs.PlateCarree())
        ax.xaxis.set_major_formatter(LongitudeFormatter())
        ax.yaxis.set_major_formatter(LatitudeFormatter())
        ax.tick_params(axis='both', labelsize=tick_label_fontsize)

        start_date = pd.to_datetime(start).strftime('%B %d, %Y')
        ax.set_title(f"{start_date}", fontsize=title_fontsize)

        start_time_str_filename = pd.to_datetime(start).strftime('%Y%m%d')
        end_time_str_filename = pd.to_datetime(end).strftime('%Y%m%d')
        filename = f"wind_vector_{start_date}.png"
        save_path = os.path.join(SAVE_DIR, filename)
        plt.savefig(save_path, dpi=500, bbox_inches='tight')
        plt.close(fig)
        print(f"Saved plot to {save_path}")
