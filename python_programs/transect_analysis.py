import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np
from scipy.interpolate import griddata

# Define directories and paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'acrobat', 'transects', 'processed')
ACROBAT_DIR = os.path.join(DATA_DIR, 'processed_dataset.csv')

CSV_SAVE_DIR = os.path.join(DATA_DIR)
if not os.path.exists(CSV_SAVE_DIR):
    os.makedirs(CSV_SAVE_DIR)
CSV_SAVE_PATH = os.path.join(CSV_SAVE_DIR, 'oc_params_by_depth.csv')

VISUAL_SAVE_DIR = os.path.join(SCRIPT_DIR, '..', 'visualization', 'transect_analysis')
if not os.path.exists(VISUAL_SAVE_DIR):
    os.makedirs(VISUAL_SAVE_DIR)

SAVE_DIR = os.path.join(DATA_DIR)
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)
STATS_SAVE_PATH = os.path.join(SAVE_DIR, 'oc_params_stats.csv')

EARTH_RADIUS = 6371  # in kilometers
INTERPOLATION_METHOD = 'cubic'  # Change to 'cubic' or 'nearest' as needed
WINDOW_SIZE = 100  # Define the window size for the rolling mean
SHORE_POINT = (-77.802938, 34.195220)

# Load the dataset
print("Loading data...")
data = pd.read_csv(ACROBAT_DIR)
print("Data loaded successfully.")

# Define the depth bins and labels
depth_bins = [0, 2, 4, 6, 8, 10]
depth_labels = [f'{int(depth_bins[i])}-{int(depth_bins[i+1])} m' for i in range(len(depth_bins)-1)]
data['depth_range'] = pd.cut(data['depth'], bins=depth_bins, labels=depth_labels, right=False)

# Add an overall range 0-10
data['overall_range'] = '0-10'

# Define parameters to plot and their units
variables_to_plot = {
    'temp': 'Temperature (°C)',
    'salinity': 'Salinity (psu)',
    'turbidity': 'Turbidity (NTU)',
    'chlor_a': 'Chlorophyll-a (µg/L)',
    'do': 'Dissolved Oxygen (mg/L)',
    'density': 'Density (kg/m³)'
}

# Function to create and save box plots
def create_and_save_plots(data, variable, unit, save_dir):
    plt.figure(figsize=(25, 15))
    ax = sns.boxplot(data=data, x='transect_id', y=variable, hue='depth_range', palette='viridis')
    plt.title(f'{variable.capitalize()} Distribution Across Transects and Depth', fontsize=26)
    plt.xlabel('Transect ID', fontsize=25)
    plt.ylabel(unit, fontsize=25)
    plt.legend(title='Depth Category', loc='best', fancybox=True, shadow=False, fontsize=20, title_fontsize=22)
    plt.grid(True)
    
    if variable == 'density':
        ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    
    plot_path = os.path.join(save_dir, f'{variable}.png')
    plt.xticks(fontsize=24)
    plt.yticks(fontsize=24)
    plt.savefig(plot_path, dpi=500, bbox_inches='tight')
    plt.close()

# Generate plots for each variable
sns.set_context("talk")
for variable, unit in variables_to_plot.items():
    create_and_save_plots(data, variable, unit, VISUAL_SAVE_DIR)
    print(f"Completed plotting for {variable}.")

# Calculate and save average parameters by depth
rows_list = []
grouped_by_depth = data.groupby('depth_range', observed=True)  # Explicitly specify observed=True
for depth_range, group in grouped_by_depth:
    stats = {
        'depth_range': depth_range,
        **{f'avg_{param}': group[param].mean() for param in variables_to_plot.keys()}
    }
    rows_list.append(stats)

grouped_overall = data.groupby('overall_range', observed=True)  # Explicitly specify observed=True
for overall_range, group in grouped_overall:
    stats = {
        'depth_range': overall_range,
        **{f'avg_{param}': group[param].mean() for param in variables_to_plot.keys()}
    }
    rows_list.append(stats)

results_df = pd.DataFrame(rows_list)
results_df.to_csv(CSV_SAVE_PATH, index=False)
print(f"Average parameters by depth CSV file has been written to {CSV_SAVE_PATH}")

# Function to calculate distance from shore using the Haversine formula
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return c * EARTH_RADIUS

# Calculate buoyancy frequency squared (N²)
g = 9.81  # Gravity in m/s²
rho0 = data['density'].mean()  # Reference density

# Compute density gradient (dρ/dz)
data['d_density_dz'] = data.groupby('transect_id')['density'].diff() / data.groupby('transect_id')['depth'].diff()

# Compute buoyancy frequency squared (N²)
data['N2'] = - (g / rho0) * data['d_density_dz']

# Apply rolling mean to smooth N² values
data['N2_smoothed'] = data.groupby('transect_id')['N2'].transform(lambda x: x.rolling(window=WINDOW_SIZE, min_periods=1).mean())

# Filter out NaN values in N²
data = data[np.isfinite(data['N2_smoothed'])]

# Calculate distances from shore for each transect
transects = data['transect_id'].unique()
distances_from_shore = []
for transect in transects:
    transect_data = data[data['transect_id'] == transect]
    middle_idx = len(transect_data) // 2
    middle_lat, middle_lon = transect_data.iloc[middle_idx][['lat', 'lon']]
    distance_from_shore = haversine(SHORE_POINT[0], SHORE_POINT[1], middle_lon, middle_lat)
    distances_from_shore.append((transect, distance_from_shore))

# Sort transects by distance from shore
distances_from_shore.sort(key=lambda x: x[1])

# Prepare data for contour plot
xi = []
yi = []
zi = []
transect_labels = []
for transect, distance in distances_from_shore:
    transect_data = data[data['transect_id'] == transect]
    xi.extend([distance] * len(transect_data))
    yi.extend(transect_data['depth'])
    zi.extend(transect_data['N2_smoothed'])
    transect_labels.append(transect)

# Create a grid for interpolation
xi = np.array(xi)
yi = np.array(yi)
zi = np.array(zi)
grid_x, grid_y = np.meshgrid(np.linspace(min(xi), max(xi), 100), np.linspace(min(yi), max(yi), 100))
grid_z = griddata((xi, yi), zi, (grid_x, grid_y), method=INTERPOLATION_METHOD)

# Plotting
fig, ax1 = plt.subplots(figsize=(16, 8))
contour = ax1.contourf(grid_x, grid_y, grid_z, levels=100, cmap='viridis')
cbar = plt.colorbar(contour, label='Buoyancy Frequency Squared (N²) (s⁻²)')
ax1.set_title('Buoyancy Frequency Squared (N²) Across Transects', fontsize=20)
ax1.set_xlabel('Distance from Shore (km)', fontsize=16)
ax1.set_ylabel('Depth (m)', fontsize=16)
ax1.invert_yaxis()  # Invert y-axis to have depth increasing downwards
ax1.grid(True)

# Create secondary x-axis for transect IDs
ax2 = ax1.twiny()
ax2.set_xlim(ax1.get_xlim())
ax2.set_xticks([dist for transect, dist in distances_from_shore])
ax2.set_xticklabels([transect for transect, dist in distances_from_shore])
ax2.set_xlabel('Transect ID', fontsize=16)

# Save the plot
plot_path = os.path.join(VISUAL_SAVE_DIR, 'N2.png')
plt.savefig(plot_path, dpi=300, bbox_inches='tight')

# Analyze stability
positive_N2 = data['N2_smoothed'][data['N2_smoothed'] > 0]
negative_N2 = data['N2_smoothed'][data['N2_smoothed'] < 0]

total_points = len(data['N2_smoothed'])
stable_percentage = len(positive_N2) / total_points * 100
unstable_percentage = len(negative_N2) / total_points * 100

mean_N2 = data['N2_smoothed'].mean()
std_N2 = data['N2_smoothed'].std()

print(f"Total data points: {total_points}")
print(f"Stable (positive N²) percentage: {stable_percentage:.2f}%")
print(f"Unstable (negative N²) percentage: {unstable_percentage:.2f}%")
print(f"Mean N²: {mean_N2:.4e}")
print(f"Standard deviation of N²: {std_N2:.4e}")

# Plot histogram of N² values
plt.figure(figsize=(14, 8))
plt.hist(data['N2_smoothed'], bins=50, color='blue', alpha=0.7)
plt.axvline(0, color='red', linestyle='--')
plt.title('Distribution of Buoyancy Frequency Squared (N²) Values')
plt.xlabel('N² (s⁻²)')
plt.ylabel('Frequency')
plt.grid(True)
hist_plot_path = os.path.join(VISUAL_SAVE_DIR, 'N2_distribution.png')
plt.savefig(hist_plot_path, dpi=300, bbox_inches='tight')

print(f"Histogram of N² values has been saved to {hist_plot_path}")

# Calculate mean parameter measurement for transects 1-7
transect_1_7_mean = data[data['transect_id'].isin(range(1, 8))].groupby('transect_id')[list(variables_to_plot.keys())].mean()

# Function to create line graph for each variable
def create_line_graph(data, variable, unit):
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data[variable], marker='o', linestyle='-', color='b')
    plt.title(f'Mean {variable.capitalize()} from Transect 1 to Transect 7')
    plt.xlabel('Transect ID')
    plt.ylabel(unit)
    plt.grid(True)

    # Remove scientific notation
    ax = plt.gca()
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False, useMathText=False))
    plt.xticks(data.index)
    plt.savefig(os.path.join(VISUAL_SAVE_DIR, f'{variable}_mean_transect_1_to_7.png'), dpi=300, bbox_inches='tight')
    plt.close()

# Generate line graph for each variable
for variable, unit in variables_to_plot.items():
    create_line_graph(transect_1_7_mean, variable, unit)
    print(f"Line graph for {variable} created.")

print("All line graphs created successfully.")

# Calculate and save statistics for each parameter
parameters = ['temp', 'density', 'salinity', 'turbidity', 'do', 'chlor_a']
rows_list = []

for parameter in parameters:
    grouped = data.groupby(['transect_id', 'depth_range'], observed=True)
    grouped_overall = data.groupby(['transect_id', 'overall_range'], observed=True)

    for group_key, group in grouped:
        transect_id, depth_range = group_key
        stats = {
            'transect_id': transect_id,
            'depth_range': depth_range,
            **{f'mean_{parameter}': group[parameter].mean(),
               f'median_{parameter}': group[parameter].median(),
               f'min_{parameter}': group[parameter].min(),
               f'max_{parameter}': group[parameter].max(),
               f'std_dev_{parameter}': group[parameter].std()}
        }
        rows_list.append(stats)

    for group_key, group in grouped_overall:
        transect_id, overall_range = group_key
        stats.update({
            'transect_id': transect_id,
            'depth_range': overall_range,
            **{f'mean_{parameter}': group[parameter].mean(),
               f'median_{parameter}': group[parameter].median(),
               f'min_{parameter}': group[parameter].min(),
               f'max_{parameter}': group[parameter].max(),
               f'std_dev_{parameter}': group[parameter].std()}
        })
        rows_list.append(stats)

results_df = pd.DataFrame(rows_list)
results_df.to_csv(STATS_SAVE_PATH, index=False)
print(f"Statistics CSV file has been written to {STATS_SAVE_PATH}")
