import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np
from scipy.interpolate import griddata
from scipy.stats import f_oneway, ttest_ind, shapiro, levene

# Define directories and paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'acrobat', 'transects', 'processed')
ACROBAT_DIR = os.path.join(DATA_DIR, 'processed_dataset.csv')
CSV_SAVE_PATH = os.path.join(DATA_DIR, 'oc_params_by_depth.csv')
VISUAL_SAVE_DIR = os.path.join(SCRIPT_DIR, '..', 'visualization', 'transect_analysis')
STATS_SAVE_PATH = os.path.join(DATA_DIR, 'oc_params_stats.csv')

# Create directories if they don't exist
os.makedirs(os.path.dirname(CSV_SAVE_PATH), exist_ok=True)
os.makedirs(VISUAL_SAVE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(STATS_SAVE_PATH), exist_ok=True)

EARTH_RADIUS = 6371  # in kilometers
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

# Function to get p-value label
def get_p_value_label(p_value):
    if p_value < 0.001:
        return 'p-value < 0.001'
    elif p_value < 0.01:
        return 'p-value < 0.01'
    elif p_value < 0.05:
        return 'p-value < 0.05'
    else:
        return 'p-value > 0.05'

# Function to create and save box plots
def create_and_save_plots(data, variable, unit, save_dir, anova_results, t_test_results):
    plt.figure(figsize=(25, 15))
    ax = sns.boxplot(data=data, x='transect_id', y=variable, hue='depth_range', palette='viridis')
    plt.title(f'{variable.capitalize()} Distribution Across Transects and Depth', fontsize=26)
    plt.xlabel('Transect ID', fontsize=25)
    plt.ylabel(unit, fontsize=25)
    plt.grid(True)
    if variable == 'density':
        ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    
    # Annotate with ANOVA p-values and T-test p-values
    anova_p_value = anova_results.get(f'mean_{variable}', {}).get('p-value', None)
    t_test_p_value = t_test_results.get(f'mean_{variable}', {}).get('p-value', None)
    handles, labels = ax.get_legend_handles_labels()
    if anova_p_value is not None:
        handles.append(plt.Line2D([], [], color='w', label=f'ANOVA {get_p_value_label(anova_p_value)}'))
    if t_test_p_value is not None:
        handles.append(plt.Line2D([], [], color='w', label=f'T-test {get_p_value_label(t_test_p_value)}'))
    ax.legend(handles=handles, title='Depth Category', loc='best', fontsize=20, title_fontsize=22)
    
    plt.xticks(fontsize=24)
    plt.yticks(fontsize=24)
    plt.savefig(os.path.join(save_dir, f'{variable}.png'), dpi=500, bbox_inches='tight')
    plt.close()

# Generate plots for each variable
sns.set_context("talk")
for variable, unit in variables_to_plot.items():
    create_and_save_plots(data, variable, unit, VISUAL_SAVE_DIR, {}, {})
    print(f"Completed plotting for {variable}.")

# Calculate and save average parameters by depth
numeric_cols = data.select_dtypes(include=[np.number]).columns
avg_params_by_depth = data.groupby('depth_range')[numeric_cols].mean().reset_index()
avg_params_by_depth.to_csv(CSV_SAVE_PATH, index=False)
print(f"Average parameters by depth CSV file has been written to {CSV_SAVE_PATH}")

# Function to calculate distance from shore using the Haversine formula
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    return 2 * EARTH_RADIUS * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

# Calculate buoyancy frequency squared (N²)
g, rho0 = 9.81, data['density'].mean()
data['d_density_dz'] = data.groupby('transect_id')['density'].diff() / data.groupby('transect_id')['depth'].diff()
data['N2'] = - (g / rho0) * data['d_density_dz']
data['N2_smoothed'] = data.groupby('transect_id')['N2'].transform(lambda x: x.rolling(window=WINDOW_SIZE, min_periods=1).mean())
data = data[np.isfinite(data['N2_smoothed'])]

# Calculate distances from shore for each transect
distances_from_shore = [(transect, haversine(SHORE_POINT[0], SHORE_POINT[1], group['lon'].median(), group['lat'].median())) for transect, group in data.groupby('transect_id')]
distances_from_shore.sort(key=lambda x: x[1])

# Prepare data for contour plot
xi, yi, zi = zip(*[(dist, depth, n2) for transect, dist in distances_from_shore for depth, n2 in zip(data[data['transect_id'] == transect]['depth'], data[data['transect_id'] == transect]['N2_smoothed'])])
grid_x, grid_y = np.meshgrid(np.linspace(min(xi), max(xi), 100), np.linspace(min(yi), max(yi), 100))
grid_z = griddata((xi, yi), zi, (grid_x, grid_y), method='cubic')

# Plotting
fig, ax1 = plt.subplots(figsize=(16, 8))
contour = ax1.contourf(grid_x, grid_y, grid_z, levels=100, cmap='viridis')
cbar = plt.colorbar(contour, label='Buoyancy Frequency Squared (N²) (s⁻²)')
ax1.set_title('Buoyancy Frequency Squared (N²) Across Transects', fontsize=20)
ax1.set_xlabel('Distance from Shore (km)', fontsize=16)
ax1.set_ylabel('Depth (m)', fontsize=16)
ax1.invert_yaxis()
ax1.grid(True)
ax2 = ax1.twiny()
ax2.set_xlim(ax1.get_xlim())
ax2.set_xticks([dist for transect, dist in distances_from_shore])
ax2.set_xticklabels([transect for transect, dist in distances_from_shore])
ax2.set_xlabel('Transect ID', fontsize=16)
plt.savefig(os.path.join(VISUAL_SAVE_DIR, 'N2.png'), dpi=300, bbox_inches='tight')

# Analyze stability
positive_N2, negative_N2 = data['N2_smoothed'][data['N2_smoothed'] > 0], data['N2_smoothed'][data['N2_smoothed'] < 0]
total_points = len(data['N2_smoothed'])
print(f"Total data points: {total_points}")
print(f"Stable (positive N²) percentage: {len(positive_N2) / total_points * 100:.2f}%")
print(f"Unstable (negative N²) percentage: {len(negative_N2) / total_points * 100:.2f}%")
print(f"Mean N²: {data['N2_smoothed'].mean():.4e}")
print(f"Standard deviation of N²: {data['N2_smoothed'].std():.4e}")

# Plot histogram of N² values
plt.figure(figsize=(14, 8))
plt.hist(data['N2_smoothed'], bins=50, color='blue', alpha=0.7)
plt.axvline(0, color='red', linestyle='--')
plt.title('Distribution of Buoyancy Frequency Squared (N²) Values')
plt.xlabel('N² (s⁻²)')
plt.ylabel('Frequency')
plt.grid(True)
plt.savefig(os.path.join(VISUAL_SAVE_DIR, 'N2_distribution.png'), dpi=300, bbox_inches='tight')

# Calculate mean parameter measurement for transects 1-7
transect_1_7_mean = data[data['transect_id'].isin(range(1, 8))].groupby('transect_id')[list(variables_to_plot.keys())].mean()

# Function to create line graph for each variable
def create_line_graph(data, variable, unit, t_test_results):
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data[variable], marker='o', linestyle='-', color='b')
    plt.title(f'Mean {variable.capitalize()} from Transect 1 to Transect 7')
    plt.xlabel('Transect ID')
    plt.ylabel(unit)
    plt.grid(True)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False, useMathText=False))
    plt.xticks(data.index)
    
    # Annotate with T-test results
    t_test_result = t_test_results.get(f'mean_{variable}', {}).get('p-value', None)
    if t_test_result is not None:
        plt.annotate(f'T-test {get_p_value_label(t_test_result)}', xy=(0.5, 0.95), xycoords='axes fraction', ha='center', fontsize=12, color='red')

    plt.savefig(os.path.join(VISUAL_SAVE_DIR, f'{variable}_mean_transect_1_to_7.png'), dpi=300, bbox_inches='tight')
    plt.close()

# Generate line graph for each variable
for variable, unit in variables_to_plot.items():
    create_line_graph(transect_1_7_mean, variable, unit, {})
    print(f"Line graph for {variable} created.")

print("All line graphs created successfully.")

# Calculate and save statistics for each parameter
rows_list = []
for parameter in variables_to_plot.keys():
    for group_key, group in data.groupby(['transect_id', 'depth_range']):
        transect_id, depth_range = group_key
        stats = {
            'transect_id': transect_id,
            'depth_range': depth_range,
            f'mean_{parameter}': group[parameter].mean(),
            f'median_{parameter}': group[parameter].median(),
            f'min_{parameter}': group[parameter].min(),
            f'max_{parameter}': group[parameter].max(),
            f'std_dev_{parameter}': group[parameter].std()
        }
        rows_list.append(stats)
    for group_key, group in data.groupby(['transect_id', 'overall_range']):
        transect_id, overall_range = group_key
        stats.update({
            'transect_id': transect_id,
            'depth_range': overall_range,
            f'mean_{parameter}': group[parameter].mean(),
            f'median_{parameter}': group[parameter].median(),
            f'min_{parameter}': group[parameter].min(),
            f'max_{parameter}': group[parameter].max(),
            f'std_dev_{parameter}': group[parameter].std()
        })
        rows_list.append(stats)

results_df = pd.DataFrame(rows_list)
results_df.to_csv(STATS_SAVE_PATH, index=False)
print(f"Statistics CSV file has been written to {STATS_SAVE_PATH}")

anova_results = {}
t_test_results = {}

# Perform significance tests
data_stats = pd.read_csv(STATS_SAVE_PATH)
transects_1_to_7 = data_stats[data_stats['transect_id'].isin(range(1, 8))]

print("\nNormality test (Shapiro-Wilk test):")
for param in variables_to_plot.keys():
    stat, p = shapiro(transects_1_to_7[f'mean_{param}'].dropna())
    print(f'Shapiro-Wilk test for mean_{param}: statistic={stat}, p-value={p}')

print("\nLevene's test for homogeneity of variances:")
for param in variables_to_plot.keys():
    stat, p = levene(*[group[f'mean_{param}'].dropna() for name, group in transects_1_to_7.groupby('transect_id')])
    print(f"Levene's test for mean_{param}: statistic={stat}, p-value={p}")

print("\nNormality and Equality of Variances for T-test:")
for param in variables_to_plot.keys():
    shallow_data = transects_1_to_7[transects_1_to_7['depth_range'] == '0-2 m'][f'mean_{param}'].dropna()
    deep_data = transects_1_to_7[transects_1_to_7['depth_range'] == '8-10 m'][f'mean_{param}'].dropna()
    stat_shallow, p_shallow = shapiro(shallow_data)
    stat_deep, p_deep = shapiro(deep_data)
    stat, p = levene(shallow_data, deep_data)
    print(f'Shapiro-Wilk test for mean_{param} (shallow): statistic={stat_shallow}, p-value={p_shallow}')
    print(f'Shapiro-Wilk test for mean_{param} (deep): statistic={stat_deep}, p-value={p_deep}')
    print(f"Levene's test for mean_{param}: statistic={stat}, p-value={p}")

print("\nANOVA results across transects:")
for param in variables_to_plot.keys():
    transect_groups = [group[f'mean_{param}'].dropna() for name, group in transects_1_to_7.groupby('transect_id')]
    f_val, p_val = f_oneway(*transect_groups)
    anova_results[f'mean_{param}'] = {'F-value': f_val, 'p-value': p_val}
    print(f"ANOVA results for mean_{param}: F-value = {f_val}, p-value = {p_val}")

print("\nT-test results between shallow (0-2m) and deep (8-10m) depth bins:")
for param in variables_to_plot.keys():
    shallow_data = transects_1_to_7[transects_1_to_7['depth_range'] == '0-2 m'][f'mean_{param}'].dropna()
    deep_data = transects_1_to_7[transects_1_to_7['depth_range'] == '8-10 m'][f'mean_{param}'].dropna()
    t_stat, p_val = ttest_ind(shallow_data, deep_data, equal_var=False)
    t_test_results[f'mean_{param}'] = {'t-statistic': t_stat, 'p-value': p_val}
    print(f"T-test results for mean_{param} between shallow and deep depths: t-statistic = {t_stat}, p-value = {p_val}")

# Generate plots for each variable with ANOVA results and T-test results in legend
for variable, unit in variables_to_plot.items():
    create_and_save_plots(data, variable, unit, VISUAL_SAVE_DIR, anova_results, t_test_results)
    print(f"Completed plotting for {variable}.")

# Generate line graph for each variable with T-test results
for variable, unit in variables_to_plot.items():
    create_line_graph(transect_1_7_mean, variable, unit, t_test_results)
    print(f"Line graph for {variable} created.")

print("All line graphs created successfully.")
