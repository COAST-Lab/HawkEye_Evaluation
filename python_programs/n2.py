import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

# Define constants and directory setup
EARTH_RADIUS = 6371  # in kilometers
INTERPOLATION_METHOD = 'linear'  # Change to 'cubic' or 'nearest' as needed
WINDOW_SIZE = 100  # Define the window size for the rolling mean
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'acrobat', 'transects', 'processed')
ACROBAT_DIR = os.path.join(DATA_DIR, 'processed_dataset.csv')
VISUAL_SAVE_DIR = os.path.join(SCRIPT_DIR, '..', 'visualization', 'depth_distributions')
if not os.path.exists(VISUAL_SAVE_DIR):
    os.makedirs(VISUAL_SAVE_DIR)

# Function to calculate distance from shore using the Haversine formula
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return c * EARTH_RADIUS

# Load the dataset
print("Loading data...")
data = pd.read_csv(ACROBAT_DIR)
print("Data loaded successfully.")

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

# Define the shore point
SHORE_POINT = (-77.802938, 34.195220)

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
plot_path = os.path.join(VISUAL_SAVE_DIR, 'N2_across_transects_with_distance_and_ids_smoothed.png')
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
plt.show()

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
plt.title('Distribution of Buoyancy Frequency Squared (N²) Values (Smoothed)')
plt.xlabel('N² (s⁻²)')
plt.ylabel('Frequency')
plt.grid(True)
hist_plot_path = os.path.join(VISUAL_SAVE_DIR, 'N2_distribution_smoothed.png')
plt.savefig(hist_plot_path, dpi=300, bbox_inches='tight')
plt.show()

print(f"Histogram of N² values has been saved to {hist_plot_path}")
