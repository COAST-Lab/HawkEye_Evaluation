import pandas as pd

# Path to the dataset
data_path = '/Users/mitchtork/Thesis/data/acrobat/transects/processed/processed_dataset.csv'

# Load the dataset
data = pd.read_csv(data_path)

# Define the depth bins including the overall range
depth_bins = [0, 2, 4, 6, 8, 10]
depth_labels = ['0-2', '2-4', '4-6', '6-8', '8-10']
data['depth_range'] = pd.cut(data['depth'], bins=depth_bins, labels=depth_labels, right=False, include_lowest=True)

# Add an overall range 0-10
data['overall_range'] = '0-10'

parameters = ['temp', 'density', 'salinity', 'turbidity', 'ox_sat', 'chlor_a']

# Initialize an empty list to collect DataFrame rows
rows_list = []

# Loop through each parameter to calculate stats
for parameter in parameters:
    # Group by transect_id and depth range
    grouped = data.groupby(['transect_id', 'depth_range'])

    # Calculate the statistics for each group and collect rows
    for (transect_id, depth_range), group in grouped:
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

    # Group by transect_id and overall range for depth 0-10
    grouped_overall = data.groupby(['transect_id', 'overall_range'])

    for (transect_id, overall_range), group in grouped_overall:
        stats = {
            'transect_id': transect_id,
            'depth_range': overall_range,
            **{f'mean_{parameter}': group[parameter].mean(),
               f'median_{parameter}': group[parameter].median(),
               f'min_{parameter}': group[parameter].min(),
               f'max_{parameter}': group[parameter].max(),
               f'std_dev_{parameter}': group[parameter].std()}
        }
        rows_list.append(stats)

# Convert list of dicts to DataFrame
results_df = pd.DataFrame(rows_list)

# Count the number of measurements per transect and calculate the average
measurements_count = data.groupby('transect_id').size()
average_measurements = measurements_count.mean()

# Define output path for the CSV file
output_csv_path = '/Users/mitchtork/Thesis/data/acrobat/transects/processed/oceanic_params_stats.csv'

# Write the results DataFrame to CSV
results_df.to_csv(output_csv_path, index=False)

print(f"Statistics CSV file has been written to {output_csv_path}")
print("Average number of measurements per transect:", average_measurements)
