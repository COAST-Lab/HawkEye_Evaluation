import numpy as np
import pandas as pd
from scipy.ndimage import generic_filter
import os

def apply_sliding_window_aggregation(data, window_size):
    """Apply sliding window averaging over a 2D grid, ignoring NaN values."""
    if window_size == 1:  # No aggregation needed for 1x1, return original data
        return data
    return generic_filter(data, np.nanmean, size=(window_size, window_size), mode='constant', cval=np.NaN)

def populate_grid(df, value_column, irow_column, icol_column, grid_shape):
    """Populate a grid with values from a DataFrame based on specified row and column indices."""
    grid = np.full(grid_shape, np.nan)
    for _, row in df.iterrows():
        irow = int(row[irow_column])
        icol = int(row[icol_column])
        if 0 <= irow < grid_shape[0] and 0 <= icol < grid_shape[1]:
            grid[irow, icol] = row[value_column]
    return grid

# Load the dataset
df = pd.read_csv('/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/satsitu.csv')

# Determine the grid size based on the maximum irow and icol for Hawkeye data
max_irow = int(df['hawkeye_irow'].max()) + 1
max_icol = int(df['hawkeye_icol'].max()) + 1
grid_shape = (max_irow, max_icol)

# Populate grids for Hawkeye and in situ measurements
hawkeye_grid = populate_grid(df, 'hawkeye_chl', 'hawkeye_irow', 'hawkeye_icol', grid_shape)
insitu_grid = populate_grid(df, 'in_situ_chl', 'hawkeye_irow', 'hawkeye_icol', grid_shape)

# Window sizes for aggregation, including 1x1 for original data
window_sizes = [1, 2, 3]

# Perform sliding window aggregations and map results back to the DataFrame
for window_size in window_sizes:
    # Apply sliding window aggregation
    aggregated_hawkeye = apply_sliding_window_aggregation(hawkeye_grid, window_size)
    aggregated_insitu = apply_sliding_window_aggregation(insitu_grid, window_size)
    
    # Flatten aggregated grids for easier indexing
    flat_hawkeye = aggregated_hawkeye.flatten()
    flat_insitu = aggregated_insitu.flatten()

    # Initialize new columns in df for aggregated values
    df[f'hawkeye_chl_{window_size}x{window_size}'] = np.nan
    df[f'insitu_chl_{window_size}x{window_size}'] = np.nan

    # Map aggregated values back to DataFrame
    for index, row in df.iterrows():
        flat_index = int(row['hawkeye_irow']) * max_icol + int(row['hawkeye_icol'])
        if 0 <= flat_index < len(flat_hawkeye):
            df.at[index, f'hawkeye_chl_{window_size}x{window_size}'] = flat_hawkeye[flat_index]
        if 0 <= flat_index < len(flat_insitu):
            df.at[index, f'insitu_chl_{window_size}x{window_size}'] = flat_insitu[flat_index]

# Output directory
output_dir = '/Users/mitchtork/HawkEye_Evaluation/data/satsitu/aggregated_data/'

# Check if output directory exists, if not, create it
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Save the processed DataFrame to a new CSV file in the output directory
output_filename = os.path.join(output_dir, 'hawkeye.csv')
df.to_csv(output_filename, index=False)
