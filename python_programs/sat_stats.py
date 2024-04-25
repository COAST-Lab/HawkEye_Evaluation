import os
import numpy as np
from netCDF4 import Dataset

# Set the directory containing the L3 NetCDF files
data_directory = '/Users/mitchtork/Thesis/data/sat_default/all_l3'

# Function to read and analyze chlor_a-mean data
def analyze_chlor_a_mean(directory):
    # List all files in the directory
    files = [f for f in os.listdir(directory) if f.endswith('.nc')]
    
    # Iterate over each file
    for filename in files:
        file_path = os.path.join(directory, filename)
        
        # Open the NetCDF file
        with Dataset(file_path, 'r') as nc:
            # Navigate to the 'Mapped_Data_and_Params' group
            if 'Mapped_Data_and_Params' in nc.groups and 'chlor_a-mean' in nc.groups['Mapped_Data_and_Params'].variables:
                chlor_a_mean = nc.groups['Mapped_Data_and_Params'].variables['chlor_a-mean'][:]
                # Compute statistics ignoring NaN values
                mean_val = np.nanmean(chlor_a_mean)
                min_val = np.nanmin(chlor_a_mean)
                max_val = np.nanmax(chlor_a_mean)
                std_dev_val = np.nanstd(chlor_a_mean)
                
                print(f"File: {filename}")
                print(f"Mean Chlorophyll-a: {mean_val} mg/m^3")
                print(f"Min Chlorophyll-a: {min_val} mg/m^3")
                print(f"Max Chlorophyll-a: {max_val} mg/m^3")
                print(f"Standard Deviation Chlorophyll-a: {std_dev_val} mg/m^3\n")
            else:
                print(f"File: {filename} does not contain 'chlor_a-mean' variable in 'Mapped_Data_and_Params' group.")

# Call the function
analyze_chlor_a_mean(data_directory)
