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

# Group by depth_range and calculate averages for each parameter across all transects
grouped_by_depth = data.groupby('depth_range')
for depth_range, group in grouped_by_depth:
    stats = {
        'depth_range': depth_range,
        **{f'avg_{param}': group[param].mean() for param in parameters}
    }
    rows_list.append(stats)

# Group by overall_range and calculate averages for each parameter across all transects
grouped_overall = data.groupby('overall_range')
for overall_range, group in grouped_overall:
    stats = {
        'depth_range': overall_range,
        **{f'avg_{param}': group[param].mean() for param in parameters}
    }
    rows_list.append(stats)

# Convert list of dicts to DataFrame
results_df = pd.DataFrame(rows_list)

# Define output path for the CSV file
output_csv_path = '/Users/mitchtork/Thesis/data/acrobat/transects/processed/average_params_by_depth.csv'

# Write the results DataFrame to CSV
results_df.to_csv(output_csv_path, index=False)

print(f"Average parameters by depth CSV file has been written to {output_csv_path}")
