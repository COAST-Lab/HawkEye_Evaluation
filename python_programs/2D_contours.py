import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from scipy.interpolate import griddata, interp1d
import cmocean
import rasterio
from geopy.distance import great_circle
from tqdm import tqdm
from matplotlib.ticker import FormatStrFormatter
from matplotlib.colors import LogNorm

INTERPOLATION_METHOD = 'linear'     # options are linear, cubic, or nearest.
DATA_TYPE = 'ox_sat'               # options are temp, salinity, density, turbidity, cdom, chlor_a, ox_sat.

SHOW_TRANSECT_TITLE = True          # Set to False to hide transect titles.
SHOW_AXES_TITLES = True             # Set to False to hide axes titles.
SHOW_COLORBAR = False               # Set to False to hide the colorbar.
ENABLE_CONTOUR_OVERLAY = False      # Set to False to disable contour overlay.
CONTOUR_LEVELS = {
    'temp': [20, 25],
    'salinity': [35],
    'density': [1025],
    'turbidity': [5.0],
    'chlor_a': [1.0]
}
ENABLE_INTERPOLATION = True         # Set to False to disable data interpolation.
ENABLE_BATHYMETRY = True            # Set to Flase to disable bathymetry data.

# Set default font sizes for all plots
plt.rcParams['font.size'] = 12  # Main font size
plt.rcParams['axes.labelsize'] = 18  # Axes label size
plt.rcParams['axes.titlesize'] = 20  # Figure title size
plt.rcParams['xtick.labelsize'] = 16  # X-tick label size
plt.rcParams['ytick.labelsize'] = 16  # Y-tick label size
plt.rcParams['figure.dpi'] = 500  # Figure resolution

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data')
ACROBAT_DIR = os.path.join(DATA_DIR, 'acrobat', 'transects', 'processed')

# Dynamically set the SAVE_DIR based on the DATA_TYPE and INTERPOLATION_METHOD
SAVE_DIR = os.path.join(SCRIPT_DIR, '..', f'visualization', 'contour_plots', 'wb', DATA_TYPE, '2D_plots', 'contour_interp', INTERPOLATION_METHOD)
if not ENABLE_INTERPOLATION:
    SAVE_DIR = os.path.join(SCRIPT_DIR, '..', f'visualization', 'contour_plots', 'wb', DATA_TYPE, '2D_plots', 'contours')

BATHYMETRY_PATH = os.path.join(SCRIPT_DIR, 'local_processing_resources', 'bathymetry', 'gebco_2023_n34.5_s33.75_w-78.0_e-77.3.tif')

NUM_CONTOUR_LEVELS = 100  # Number of contour levels in the plot
EARTH_RADIUS = 6371  # in kilometers

def haversine(lon1, lat1, lon2, lat2):
    # Calculate the great circle distance between two points on the earth (specified in decimal degrees)
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return c * EARTH_RADIUS

def get_global_min_max(file_names):
    all_mins = []
    all_maxs = []

    for fname in tqdm(file_names):
        try:
            data = pd.read_csv(fname)
            if DATA_TYPE in data.columns:
                all_mins.append(data[DATA_TYPE].min())
                all_maxs.append(data[DATA_TYPE].max())
            else:
                print(f"Warning: Column '{DATA_TYPE}' not found in {fname}. Available columns: {data.columns.tolist()}")
        except Exception as e:
            print(f"Error processing file {fname}: {e}")

    if not all_mins or not all_maxs:  # Check if lists are empty
        print("No valid data found. Check the column names and file contents.")
        return None, None  # Return None or handle accordingly

    return min(all_mins), max(all_maxs)


def load_bathymetry(file_path):
    # Load bathymetry data from a GeoTIFF file
    with rasterio.open(file_path) as src:
        bathymetry_data = src.read(1)
        transform = src.transform
    return bathymetry_data, transform

def plot_transect_gradients(file_names, bathymetry_data, transform, global_min, global_max, include_bathymetry):
    # Base plot dimensions
    base_plot_width = 10  # base width in inches
    base_plot_height = 10  # base height in inches

    # Adjust width based on additional features
    extra_width = 0
    if SHOW_COLORBAR:
        extra_width += 2  # Adding extra width for colorbar

    # Adjust width for axes titles and figure title
    if SHOW_AXES_TITLES or SHOW_TRANSECT_TITLE:
        extra_width += 1  # Adding extra width for titles

    # Set the figure size dynamically
    fig_width = base_plot_width + extra_width
    fig_height = base_plot_height  # Height remains constant

    # Plot the gradients for each transect based on DATA_TYPE
    max_distance = 0
    print(f"Generating {DATA_TYPE} gradient plots...")
    for idx, fname in enumerate(tqdm(file_names)):
        df = pd.read_csv(fname)
        
        # Add these lines to calculate and print local min and max for each transect
        local_min = df[DATA_TYPE].min()
        local_max = df[DATA_TYPE].max()
        print(f"Transect {idx + 1} - Local {DATA_TYPE.capitalize()} Min: {local_min}, Local Max: {local_max}")
       
        accumulated_distance = [0]

        # Calculate accumulated distances along the transect
        for i in range(1, len(df)):
            if i % 10 == 0:
                lon1, lat1 = df.iloc[i - 10][['lon', 'lat']]
                lon2, lat2 = df.iloc[i][['lon', 'lat']]
                distance = haversine(lon1, lat1, lon2, lat2)
                accumulated_distance.append(accumulated_distance[-1] + distance)
            else:
                accumulated_distance.append(accumulated_distance[-1])

        max_distance = max(max_distance, accumulated_distance[-1])
        df['normalized_distance'] = accumulated_distance

        # Dynamically define colormap and data label based on DATA_TYPE
        if DATA_TYPE == 'temp':
            colormap = cmocean.cm.thermal
            data_label = 'Temperature (°C)'
        elif DATA_TYPE == 'salinity':
            colormap = cmocean.cm.haline
            data_label = 'Salinity (PSU)'
        elif DATA_TYPE == 'density':
            colormap = cmocean.cm.dense
            data_label = 'Density (kg/m³)'
        elif DATA_TYPE == 'turbidity':
            colormap = cmocean.cm.turbid
            data_label = 'Turbidity (NTU)'
        elif DATA_TYPE == 'cdom':
            colormap = cmocean.cm.matter
            data_label = 'CDOM'
        elif DATA_TYPE == 'chlor_a':
            colormap = cmocean.cm.algae
            data_label = 'Chlorophyll a (µg/L)'
            # Define fixed_min and fixed_max for chlorophyll a visualization
            fixed_min = 0.1  # Minimum value for the color scale
            fixed_max = 5.5  # Maximum value for the color scale
            norm = LogNorm(vmin=fixed_min, vmax=fixed_max)  # Using LogNorm for chlor_a
        elif DATA_TYPE == 'ox_sat':
            colormap = cmocean.cm.deep
            data_label = 'Oxygen Saturation (%)'
        else:
            colormap = cmocean.cm.haline  # Default colormap
            data_label = f'{DATA_TYPE.capitalize()} value'
            
        # Initialize max_depth based on the depth data
        max_depth = df['depth'].max()

        # Interpolation setup
        num_x_points = round(len(df) / 10)
        num_y_points = round(df['depth'].nunique() / 5)

        xi = np.linspace(df['normalized_distance'].min(), df['normalized_distance'].max(), num_x_points)
        yi = np.linspace(df['depth'].min(), df['depth'].max(), num_y_points)
        xi, yi = np.meshgrid(xi, yi)

        # Calculate evenly spaced ticks for colorbar
        colorbar_ticks = np.linspace(global_min, global_max, 11)

        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        # Set the background color of the figure and axes
        fig.patch.set_facecolor('#FFFFFF')  # Set the figure's background color
        ax.set_facecolor('#FFFFFF')  # Set the axes' background color

        if ENABLE_INTERPOLATION:
            # Interpolation of the data
            zi = griddata((df['normalized_distance'], df['depth']), df[DATA_TYPE], (xi, yi), method=INTERPOLATION_METHOD)
            zi = np.ma.masked_invalid(zi)
            contour = ax.contourf(xi, yi, zi, NUM_CONTOUR_LEVELS, cmap=colormap, vmin=global_min, vmax=global_max)

            if SHOW_COLORBAR:
                cbar = plt.colorbar(contour, ticks=colorbar_ticks)
                cbar.set_label(data_label)
                cbar.ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Format colorbar labels to two decimal places

            x_max = df['normalized_distance'].max()
            ax.set_xticks(np.arange(0, x_max, 0.50))

            if ENABLE_CONTOUR_OVERLAY:
                # Check if the current data type has specified contour levels
                contour_levels = CONTOUR_LEVELS.get(DATA_TYPE, None)
                # Overlay contour lines if levels are specified
                if contour_levels:
                    CS = ax.contour(xi, yi, zi, levels=contour_levels, colors='red', linewidths=1)
        else:
            # Plot using scatter for non-interpolated data
            scatter = ax.scatter(df['normalized_distance'], df['depth'], c=df[DATA_TYPE], cmap=colormap, vmin=global_min, vmax=global_max, s=5)
            if SHOW_COLORBAR:
                cbar = plt.colorbar(scatter, ticks=colorbar_ticks, label=data_label)
                cbar.ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Optional: Format colorbar labels to two decimal places


        # Overlay a line representing the original data points
        ax.plot(df['normalized_distance'], df['depth'], color='black', linewidth=1, linestyle='dotted')

        if include_bathymetry:
            # Get start and end points of the transect
            start_lon, start_lat = df.iloc[0][['lon', 'lat']]
            end_lon, end_lat = df.iloc[-1][['lon', 'lat']]

            # Convert the lat-lon to row-col in the GeoTIFF
            col_start, row_start = map(int, ~transform * (start_lon, start_lat))
            col_end, row_end = map(int, ~transform * (end_lon, end_lat))

            # Slice the bathymetry data and interpolate it
            sliced_bathymetry_data = bathymetry_data[min(row_start, row_end):max(row_start, row_end),
                                                     min(col_start, col_end):max(col_start, col_end)].mean(axis=0)

            # Reverse the sliced bathymetry data for the new orientation
            sliced_bathymetry_data = sliced_bathymetry_data[::-1]

            f = interp1d(np.linspace(0, max_distance, len(sliced_bathymetry_data)),
                         sliced_bathymetry_data, kind='cubic')
            bathy_at_transect = f(df['normalized_distance'])

            # Ensure bathymetric depths are positive
            bathy_at_transect = np.abs(bathy_at_transect)

            # Update max_depth if necessary
            max_depth = max(max_depth, np.max(bathy_at_transect)) + 1  # Add 1 for margin

            # Plotting the bathymetric data along the bottom
            ax.plot(df['normalized_distance'], bathy_at_transect, 'k-', linewidth=2)

            # Fill the area below the bathymetric line (higher depth values)
            ax.fill_between(df['normalized_distance'], max_depth, bathy_at_transect, color='gray', alpha=0.5)

        # Adjust layout to minimize white space
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

        # Set plot limits and labels
        min_depth = 0
        ax.set_ylim([min_depth, max_depth])  # Use the calculated max_depth
        ax.invert_yaxis()

        if SHOW_AXES_TITLES:
            ax.set_xlabel('Distance along transect (km)')
            ax.set_ylabel('Depth (m)')

        if SHOW_TRANSECT_TITLE:
            ax.set_title(f'{DATA_TYPE.capitalize()} gradient of transect {idx + 1}')

        # Saving the figure with the specified DPI
        plt.savefig(f"{SAVE_DIR}/transect_{idx + 1}.png", dpi=plt.rcParams['figure.dpi'], bbox_inches='tight')
        plt.close()

def main():
    file_names = [os.path.join(ACROBAT_DIR, f'transect_{i}.csv') for i in range(1, 8)]
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    bathymetry_data, transform = load_bathymetry(BATHYMETRY_PATH) if ENABLE_BATHYMETRY else (None, None)
    print("Loading bathymetry data..." if ENABLE_BATHYMETRY else "Skipping bathymetry data...")

    global_min, global_max = get_global_min_max(file_names)
    print(f"Global {DATA_TYPE.capitalize()} Min: {global_min}, Global Max: {global_max}")

    plot_transect_gradients(file_names, bathymetry_data, transform, global_min, global_max, ENABLE_BATHYMETRY)

    print("Visualization complete. Check the output directory for plots.")

if __name__ == "__main__":
    main()
