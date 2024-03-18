import numpy as np
import pandas as pd
from scipy.ndimage import generic_filter
import os

# Dynamically set the base directory to the script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define data and output directories relative to BASE_DIR
DATA_DIR = os.path.join(BASE_DIR, 'data', 'acrobat', '050523', 'transects', 'processed_transects')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'satsitu', 'aggregated_data')


def apply_sliding_window_aggregation(data, window_size):
    # Apply sliding window averaging over a 2D grid, ignoring NaN values.
    if window_size == 1:  # No aggregation needed for 1x1, return original data
        return data
    return generic_filter(data, np.nanmean, size=(window_size, window_size), mode='constant', cval=np.NaN)

def populate_grid(df, value_column, irow_column, icol_column, grid_shape):
    # Populate a grid with values from a DataFrame based on specified row and column indices.
    grid = np.full(grid_shape, np.nan)
    for _, row in df.iterrows():
        irow = int(row[irow_column])
        icol = int(row[icol_column])
        if 0 <= irow < grid_shape[0] and 0 <= icol < grid_shape[1]:
            grid[irow, icol] = row[value_column]
    return grid

# Load the dataset
df = pd.read_csv(os.path.join(DATA_DIR, 'satsitu_l2.csv'))

# Determine the grid size based on the maximum irow and icol for s3b data
max_irow = int(df['s3b_irow'].max()) + 1
max_icol = int(df['s3b_icol'].max()) + 1
grid_shape = (max_irow, max_icol)

# Populate grids for s3b and in situ measurements
s3b_grid = populate_grid(df, 's3b_chl', 's3b_irow', 's3b_icol', grid_shape)
insitu_grid = populate_grid(df, 'in_situ_chl', 's3b_irow', 's3b_icol', grid_shape)

# Window sizes for aggregation, including 1x1 for original data
window_sizes = [1, 2, 3]

# Perform sliding window aggregations and map results back to the DataFrame
for window_size in window_sizes:
    # Apply sliding window aggregation
    aggregated_s3b = apply_sliding_window_aggregation(s3b_grid, window_size)
    aggregated_insitu = apply_sliding_window_aggregation(insitu_grid, window_size)
    
    # Initialize new columns in df for aggregated values
    df[f's3b_chl_{window_size}x{window_size}'] = np.nan
    df[f'insitu_chl_{window_size}x{window_size}'] = np.nan

    # Map aggregated values back to DataFrame
    for index, row in df.iterrows():
        flat_index = int(row['s3b_irow']) * max_icol + int(row['s3b_icol'])
        if 0 <= flat_index < len(aggregated_s3b.flatten()):
            df.at[index, f's3b_chl_{window_size}x{window_size}'] = aggregated_s3b.flatten()[flat_index]
        if 0 <= flat_index < len(aggregated_insitu.flatten()):
            df.at[index, f'insitu_chl_{window_size}x{window_size}'] = aggregated_insitu.flatten()[flat_index]

# Check if output directory exists, if not, create it
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Save the processed DataFrame to a new CSV file in the output directory
output_filename = os.path.join(OUTPUT_DIR, 's3b_l2.csv')
df.to_csv(output_filename, index=False)
