import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.mpl.ticker as cticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Load the data
df = pd.read_excel('/Users/mitchtork/HawkEye_Evaluation/data/satsitu/satellite_chl_arrays/output_file.xlsx')

# Calculate global chlorophyll min/max
global_chl_min = df['chlor_a'].min()
global_chl_max = df['chlor_a'].max()

# Get unique sensor names
sensors = df['sensor_name'].unique()

for sensor_name in sensors:
    # Filter data for this sensor
    sensor_data = df[df['sensor_name'] == sensor_name]

    # Determine the grid size
    max_row = sensor_data['irow'].max() + 1
    max_col = sensor_data['icol'].max() + 1

    # Create an empty grid
    grid = np.full((max_row, max_col), np.nan)

    # Populate the grid with chlorophyll data
    for _, row in sensor_data.iterrows():
        grid[row['irow'], row['icol']] = row['chlor_a']

    # Plotting
    plt.figure(figsize=(10, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())  # Use a simple Plate Carree projection
    ax.add_feature(cfeature.GSHHSFeature(levels=[1], facecolor='lightgray', edgecolor='black'))

    # Determine the geographic extent of the grid
    extent = [-77.85, -77.70, 34.10, 34.25]  # [west, east, south, north]

    # Plot the grid as an image
    im = ax.imshow(grid, extent=extent, origin='upper', cmap='viridis', vmin=global_chl_min, vmax=global_chl_max, transform=ccrs.PlateCarree())

    # Add a colorbar with global min/max
    plt.colorbar(im, label='Chlorophyll-a concentration (mg m^-3)')

    plt.title(f'{sensor_name} Satellite Chlorophyll Measurements')
    plt.show()
