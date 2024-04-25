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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WIND_DIR = os.path.join(SCRIPT_DIR, 'local_processing_resources', 'meteorological', 'wind', 'adaptor.mars.internal-1706121221.9677804-13631-13-0aaf00c1-19ae-407a-a7ee-7520794a10dc.nc')
SAVE_DIR = os.path.join(SCRIPT_DIR, '..', 'visualization', 'meteorological', 'wind')
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

lat_south, lon_west, lat_north, lon_east = 33.80, -78.05, 34.40, -77.45

time_windows = [
    #('2023-05-03T08:00:00', '2023-05-03T20:00:00'),
    #('2023-05-04T08:00:00', '2023-05-04T20:00:00'),
    ('2023-05-05T08:00:00', '2023-05-05T20:00:00'),
    ('2023-05-06T08:00:00', '2023-05-06T20:00:00'),
    ('2023-05-07T08:00:00', '2023-05-07T20:00:00')
]

global_min = np.inf
global_max = -np.inf

with xr.open_dataset(WIND_DIR) as ncw:
    for start, end in time_windows:
        u = ncw['u10'].sel(time=slice(start, end))
        v = ncw['v10'].sel(time=slice(start, end))
        wind_speed = np.sqrt(u**2 + v**2)

        min_wind_speed = wind_speed.min().values
        max_wind_speed = wind_speed.max().values

        global_min = min(global_min, min_wind_speed)
        global_max = max(global_max, max_wind_speed)
        print(f"Global minimum: {global_min}, Global maximum: {global_max}")

    for start, end in time_windows:
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
                                   vmin=global_min, 
                                   vmax=global_max)

        #plt.colorbar(speed_plot, ax=ax, orientation='vertical', label='Wind speed (m/s)')
        ax.quiver(lon_np, lat_np, u_np, v_np, color='black', transform=ccrs.PlateCarree())

        # Setting x and y labels
        #ax.set_xlabel('Longitude', fontsize=12)
        #ax.set_ylabel('Latitude', fontsize=12)
        xticks = np.arange(lon_west, lon_east, 0.1)
        yticks = np.arange(lat_south, lat_north, 0.1)
        ax.set_xticks(xticks, crs=ccrs.PlateCarree())
        ax.set_yticks(yticks, crs=ccrs.PlateCarree())
        ax.xaxis.set_major_formatter(LongitudeFormatter())
        ax.yaxis.set_major_formatter(LatitudeFormatter())
        ax.tick_params(axis='both', labelsize=10)

        start_time = pd.to_datetime(start)
        end_time = pd.to_datetime(end)
        start_time_str_title = start_time.strftime('%B %d, %Y %H:%M')
        end_time_str_title = end_time.strftime('%B %d, %Y %H:%M')
        ax.set_title(f"{start_time_str_title} - {end_time_str_title}")

        start_time_str_filename = start_time.strftime('%Y%m%d%H%M')
        end_time_str_filename = end_time.strftime('%Y%m%d%H%M')
        filename = f"wind_vector_{start_time_str_filename}_to_{end_time_str_filename}.png"
        save_path = os.path.join(SAVE_DIR, filename)
        plt.savefig(save_path, dpi=500, bbox_inches='tight')
        plt.close(fig)
        print(f"Saved plot to {save_path}")
