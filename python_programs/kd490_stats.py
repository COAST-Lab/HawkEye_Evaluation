import os
import numpy as np
from netCDF4 import Dataset

# Set the directory containing the L3 NetCDF files
data_directory = '/Users/mitchtork/Thesis/data/sat_default/kd490_all_l3'

# Function to read and analyze kd490 data
def analyze_kd490(directory):
    # List all files in the directory
    files = [f for f in os.listdir(directory) if f.endswith('.nc')]
    
    # Iterate over each file
    for filename in files:
        file_path = os.path.join(directory, filename)
        
        # Open the NetCDF file
        with Dataset(file_path, 'r') as nc:
            # Navigate to the 'Mapped_Data_and_Params' group
            if 'Mapped_Data_and_Params' in nc.groups:
                if 'Kd_490-mean' in nc.groups['Mapped_Data_and_Params'].variables:
                    kd490_mean = nc.groups['Mapped_Data_and_Params'].variables['Kd_490-mean'][:]
                    mean_kd490 = np.nanmean(kd490_mean)
                    min_kd490 = np.nanmin(kd490_mean)
                    max_kd490 = np.nanmax(kd490_mean)
                    std_dev_kd490 = np.nanstd(kd490_mean)
                    
                    print(f"File: {filename}")
                    print(f"Mean kd490: {mean_kd490} 1/m")
                    print(f"Min kd490: {min_kd490} 1/m")
                    print(f"Max kd490: {max_kd490} 1/m")
                    print(f"Standard Deviation kd490: {std_dev_kd490} 1/m\n")
                else:
                    print(f"File: {filename} does not contain 'Kd_490-mean' variable in 'Mapped_Data_and_Params' group.")
            else:
                print(f"File: {filename} does not contain 'Mapped_Data_and_Params' group.")

# Call the function
analyze_kd490(data_directory)
