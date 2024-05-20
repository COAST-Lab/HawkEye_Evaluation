import pandas as pd
import os

# Define directories and paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'acrobat', 'transects', 'processed')
ACROBAT_DIR = os.path.join(DATA_DIR, 'processed_dataset.csv')
SAVE_DIR = os.path.join(DATA_DIR)  # Use a dedicated directory for saving results
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)
SAVE_PATH = os.path.join(SAVE_DIR, 'oc_params_stats.csv')  # Correct file path for saving the CSV

# Load the dataset
data = pd.read_csv(ACROBAT_DIR)

# Define the depth bins including the overall range
depth_bins = [0, 2, 4, 6, 8, 10]
depth_labels = ['0-2', '2-4', '4-6', '6-8', '8-10']
data['depth_range'] = pd.cut(data['depth'], bins=depth_bins, labels=depth_labels, right=False, include_lowest=True)
data['overall_range'] = '0-10'

parameters = ['temp', 'density', 'salinity', 'turbidity', 'ox_sat', 'chlor_a']
rows_list = []

# Loop through each parameter to calculate stats
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
results_df.to_csv(SAVE_PATH, index=False)
print(f"Statistics CSV file has been written to {SAVE_PATH}")
