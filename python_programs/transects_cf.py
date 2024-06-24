import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.image as mpimg
import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data')
ACROBAT_DIR = os.path.join(DATA_DIR, 'acrobat', 'archive', '050323', 'transects', 'transect_1.csv')
SAVE_PATH = os.path.join(SCRIPT_DIR, '..', 'visualization', 'maps', 'transects_cf.png')
COMPASS_ROSE_PATH = os.path.join(SCRIPT_DIR, 'local_processing_resources', 'compass_rose.png')

def add_scale_bar(ax, length, location=(0.940, 0.075), linewidth=3, fontsize=28):
    x0, x1, y0, y1 = ax.get_extent()
    scale_length = length / 111.32
    x = x0 + (x1 - x0) * location[0]
    y = y0 + (y1 - y0) * location[1]
    ax.plot([x, x - scale_length], [y, y], transform=ccrs.Geodetic(), color='black', linewidth=linewidth)
    ax.text(x - scale_length / 2, y - 0.001, f'{length} km', verticalalignment='top', horizontalalignment='center', transform=ccrs.Geodetic(), color='black', fontsize=fontsize)

data = pd.read_csv(ACROBAT_DIR)

extent = [-78, -77.90, 34.165, 34.065]

fig, ax = plt.subplots(figsize=(20, 20), subplot_kw={'projection': ccrs.PlateCarree()})
ax.set_extent(extent)

# Add GSHHS high-resolution coastline and ocean color
ax.add_feature(cfeature.GSHHSFeature(scale='full', levels=[1], facecolor='#bdbdbd'))
ax.add_feature(cfeature.OCEAN, facecolor='#f7fbff')

# Plotting the transect
ax.plot(data['lon'], data['lat'], color='blue', label='Transect 1', transform=ccrs.Geodetic())

ax.legend(loc='lower left', fontsize=28)  # Increase legend font size
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': 32}  # Increase grid label font size
gl.ylabel_style = {'size': 32}

plt.title("Cape Fear River", fontsize=40)  # Increase title font size

new_ax = fig.add_axes([0.75, 0.75, 0.1, 0.1])
compass_rose = mpimg.imread(COMPASS_ROSE_PATH)
new_ax.imshow(compass_rose)
new_ax.axis('off')

add_scale_bar(ax, 2)  # Increase scale bar text font size

plt.savefig(SAVE_PATH, dpi=500, bbox_inches='tight')
