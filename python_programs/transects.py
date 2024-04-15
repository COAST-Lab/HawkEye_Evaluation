import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
import numpy as np
import os

# Set up directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data')
ACROBAT_DIR = os.path.join(DATA_DIR, 'acrobat', 'transects', 'processed', 'processed_dataset.csv')
SAVE_PATH = os.path.join(SCRIPT_DIR, '..', 'visualization', 'maps', 'transects_wb.png')
COMPASS_ROSE_PATH = os.path.join(SCRIPT_DIR, 'local_processing_resources', 'compass_rose.png')

def add_scale_bar(ax, length, location=(0.940, 0.075), linewidth=3):
    # Get the extent of the projected map
    x0, x1, y0, y1 = ax.get_extent()
    # Set the length of the scale bar
    scale_length = length / 111.32  # degrees per km at the equator (rough approximation)
    # Set the location
    x = x0 + (x1 - x0) * location[0]
    y = y0 + (y1 - y0) * location[1]
    # Draw the scale bar
    ax.plot([x, x - scale_length], [y, y], transform=ccrs.Geodetic(), color='black', linewidth=linewidth)
    # Label the scale bar
    ax.text(x - scale_length / 2, y - 0.005, f'{length} km', verticalalignment='top', horizontalalignment='center', transform=ccrs.Geodetic(), color='black')

data = pd.read_csv(ACROBAT_DIR)

# Define the coordinates for the bounding box
extent = [-77.85, -77.70, 34.10, 34.25]

# Set up the map
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
ax.set_extent(extent)

# Add GSHHS high-resolution coastline
ax.add_feature(cfeature.GSHHSFeature(scale='full', levels=[1], facecolor='#bdbdbd'))

# Change ocean color to a more distinct blue
ax.add_feature(cfeature.OCEAN, facecolor='#f7fbff')

transect_colors = plt.cm.viridis(np.linspace(0, 1, 7))  # Use a color map to generate 7 distinct colors
for i, transect_id in enumerate(sorted(data['transect_id'].unique())):
    transect_data = data[data['transect_id'] == transect_id]
    ax.plot(transect_data['lon'], transect_data['lat'], color=transect_colors[i], label=f'Transect {transect_id}', transform=ccrs.Geodetic())

# Add legend for transects
ax.legend(loc='upper left', title='Transects')
# Set up grid lines and tick marks
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
gl.top_labels = False
gl.right_labels = False

plt.title("RV Cape Fear, May 05 2023, Wilmington, NC")

# Add Compass Rose
new_ax = fig.add_axes([0.65, 0.75, 0.2, 0.1], anchor='NE', zorder=1)
compass_rose = mpimg.imread(COMPASS_ROSE_PATH)
new_ax.imshow(compass_rose)
new_ax.axis('off')

# Add Scale Bar
add_scale_bar(ax, 2)  # Adjust this value if necessary to reflect the actual length you desire

plt.savefig(SAVE_PATH)
