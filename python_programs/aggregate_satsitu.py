import numpy as np
import pandas as pd
from scipy.ndimage import generic_filter
import os
import warnings
from pandas.errors import PerformanceWarning

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'satsitu_l2.csv')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
output_filename = os.path.join(OUTPUT_DIR, 'combined_aggregated_satsitu_data_l2_2.csv')

df = pd.read_csv(DATA_DIR)

# Extract unique identifiers for each satellite data set, considering the column names directly
sensor_identifiers = set(col.rsplit('_', 1)[0] for col in df.columns if 'irow' in col)

# Specify the depth ranges
depth_ranges = [(0, 3), (4, 6), (7, 10), (0, 10), (0, 5), (5, 10)]

# Suppress warnings related to mean of empty slices and DataFrame fragmentation
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', category=PerformanceWarning)


def apply_sliding_window_aggregation(data, window_size):
    if window_size == 1:
        return data
    return generic_filter(data, np.nanmean, size=(window_size, window_size), mode='constant', cval=np.NaN)

def populate_grid(df, value_column, irow_column, icol_column, grid_shape):
    grid = np.full(grid_shape, np.nan)
    for _, row in df.iterrows():
        irow = int(row[irow_column])
        icol = int(row[icol_column])
        if 0 <= irow < grid_shape[0] and 0 <= icol < grid_shape[1]:
            grid[irow, icol] = row[value_column]
    return grid

def filter_by_depth_range(df, depth_col, depth_range):
    return df[(df[depth_col] >= depth_range[0]) & (df[depth_col] < depth_range[1])]

def process_sensor(df, sensor_identifier, output_dir, depth_ranges, depth_col='depth', in_situ_chl_col='chlor_a'):
    print(f"Processing {sensor_identifier}...")
    irow_col = f'{sensor_identifier}_irow'
    icol_col = f'{sensor_identifier}_icol'
    chl_col = f'{sensor_identifier}_chl'
    
    max_irow = int(df[irow_col].max()) + 1
    max_icol = int(df[icol_col].max()) + 1
    grid_shape = (max_irow, max_icol)
    
    sensor_grid = populate_grid(df, chl_col, irow_col, icol_col, grid_shape)
    
    window_sizes = [1, 2, 3]
    
    for window_size in window_sizes:
        print(f"Applying window size {window_size}x{window_size}...")
        aggregated_sensor = apply_sliding_window_aggregation(sensor_grid, window_size)
        
        flat_sensor = aggregated_sensor.flatten()
        
        df[f'{sensor_identifier}_chl_{window_size}x{window_size}'] = np.nan
        for index, row in df.iterrows():
            flat_index = int(row[irow_col]) * max_icol + int(row[icol_col])
            if 0 <= flat_index < len(flat_sensor):
                df.at[index, f'{sensor_identifier}_chl_{window_size}x{window_size}'] = flat_sensor[flat_index]

        for depth_range in depth_ranges:
            df_depth_filtered = filter_by_depth_range(df, depth_col, depth_range)
            in_situ_grid_depth_filtered = populate_grid(df_depth_filtered, in_situ_chl_col, irow_col, icol_col, grid_shape)
            
            aggregated_in_situ_depth_filtered = apply_sliding_window_aggregation(in_situ_grid_depth_filtered, window_size)
            
            flat_in_situ_depth_filtered = aggregated_in_situ_depth_filtered.flatten()
            
            depth_range_str = f'{depth_range[0]}-{depth_range[1]}m'
            column_name = f'{sensor_identifier}_insitu_chl_{depth_range_str}_{window_size}x{window_size}'
            df[column_name] = np.nan
            for index, row in df.iterrows():
                flat_index = int(row[irow_col]) * max_icol + int(row[icol_col])
                if 0 <= flat_index < len(flat_in_situ_depth_filtered):
                    df.at[index, column_name] = flat_in_situ_depth_filtered[flat_index]

# Main loop to process each sensor identifier
for sensor_identifier in sensor_identifiers:
    process_sensor(df, sensor_identifier, OUTPUT_DIR, depth_ranges)

df.to_csv(output_filename, index=False)
print("Processing completed.")