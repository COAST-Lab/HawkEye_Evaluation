import pandas as pd

# Path to your CSV file
csv_file_path = '/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/satsitu.csv'

# Load the dataset
df = pd.read_csv(csv_file_path)

# Specify the columns of interest
satellite_columns = ['hawkeye_chl', 'modisa_chl', 's3a_chl', 's3b_chl', 'oli8_chl']

# Calculate the global minimum and maximum across the specified columns
global_min = df[satellite_columns].min().min()
global_max = df[satellite_columns].max().max()

print(f'Global Minimum: {global_min}')
print(f'Global Maximum: {global_max}')
