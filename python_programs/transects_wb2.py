import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
import numpy as np
import os
import matplotlib.ticker as mticker
import xarray as xr

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data')
ACROBAT_DIR = os.path.join(DATA_DIR, 'acrobat', 'transects', 'processed', 'processed_dataset.csv')
BATHYMETRY_PATH = '/Users/mitchtork/Thesis/HawkEye_Evaluation/python_programs/local_processing_resources/bathymetry/GEBCO_11_Jul_2024_2575a68e6f70/gebco_2023_n35.0_s33.5_w-78.0_e-77.0.nc'
SAVE_PATH = os.path.join(SCRIPT_DIR, '..', 'visualization', 'maps', 'transects_wb.png')
COMPASS_ROSE_PATH = os.path.join(SCRIPT_DIR, 'local_processing_resources', 'compass_rose.png')

# Function to add scale bar to the map
def add_scale_bar(ax, length, location=(0.940, 0.075), linewidth=3):
    x0, x1, y0, y1 = ax.get_extent()
    scale_length = length / 111.32  # degrees per km at the equator (rough approximation)
    x = x0 + (x1 - x0) * location[0]
    y = y0 + (y1 - y0) * location[1]
    ax.plot([x, x - scale_length], [y, y], transform=ccrs.Geodetic(), color='black', linewidth=linewidth)
    ax.text(x - scale_length / 2, y - 0.001, f'{length} km', verticalalignment='top', horizontalalignment='center', fontsize=28, transform=ccrs.Geodetic(), color='black')

# Load transect data
data = pd.read_csv(ACROBAT_DIR)

extent = [-77.85, -77.70, 34.10, 34.25]

# Load bathymetry data
bathymetry = xr.open_dataset(BATHYMETRY_PATH)
bathymetry = bathymetry.sel(lon=slice(extent[0], extent[1]), lat=slice(extent[2], extent[3]))

fig, ax = plt.subplots(figsize=(20, 20), subplot_kw={'projection': ccrs.PlateCarree()})
ax.set_extent(extent)

# Add GSHHS high-resolution coastline
ax.add_feature(cfeature.GSHHSFeature(scale='full', levels=[1], facecolor='#bdbdbd'))
ax.add_feature(cfeature.OCEAN, facecolor='#f7fbff')

# Plot bathymetry data
lon = bathymetry['lon'].values
lat = bathymetry['lat'].values
elevation = bathymetry['elevation'].values  # Use the correct variable name
contour = ax.contour(lon, lat, elevation, levels=np.arange(-50, 0, 5), colors='blue', transform=ccrs.PlateCarree())
ax.clabel(contour, fmt='%d m', fontsize=14, inline=1, colors='blue')

# Plot transects
transect_colors = plt.cm.viridis(np.linspace(0, 1, 7))  # Use a color map to generate 7 distinct colors
for i, transect_id in enumerate(sorted(data['transect_id'].unique())):
    transect_data = data[data['transect_id'] == transect_id]
    ax.plot(transect_data['lon'], transect_data['lat'], color=transect_colors[i], label=f'Transect {transect_id}', transform=ccrs.Geodetic())

# Add legend for transects with larger font
ax.legend(loc='upper left', fontsize=28)
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
gl.top_labels = False
gl.right_labels = False
gl.xlocator = mticker.FixedLocator(np.arange(extent[0], extent[1]+0.00, 0.03))
gl.ylocator = mticker.FixedLocator(np.arange(extent[2], extent[3]+0.00, 0.03))
gl.xlabel_style = {'size': 32}
gl.ylabel_style = {'size': 32}

plt.title("Masonboro Inlet", fontsize=40)

# Add Compass Rose
new_ax = fig.add_axes([0.65, 0.75, 0.2, 0.1], anchor='NE', zorder=1)
compass_rose = mpimg.imread(COMPASS_ROSE_PATH)
new_ax.imshow(compass_rose)
new_ax.axis('off')

# Add Scale Bar
add_scale_bar(ax, 2)  # Adjust this value if necessary to reflect the actual length you desire

plt.savefig(SAVE_PATH, dpi=500, bbox_inches='tight')
