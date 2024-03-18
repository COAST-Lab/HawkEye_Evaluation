from netCDF4 import Dataset

# Path to your NetCDF file
nc_file = '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/sensors/landsat/l1a-l3/daily/30m-chlor_a/mean/LANDSAT8_OLI.2023050320230503.DLY.chlor_a.map.nc'

# Open the NetCDF file
dataset = Dataset(nc_file, 'r')

print(f"File: {nc_file}\n")

# Print global attributes
print("Global Attributes:")
for name in dataset.ncattrs():
    print(f"{name}: {dataset.getncattr(name)}")

# Checking for variables that might indicate time
print("\nVariables potentially related to time:")
for var_name, variable in dataset.variables.items():
    # Check if 'time' is in the variable name or any of its attributes suggest it could contain time information
    if 'time' in var_name.lower() or any('time' in attr.lower() for attr in variable.ncattrs()):
        print(f"Variable Name: {var_name}")
        print("Attributes:")
        for attr_name in variable.ncattrs():
            print(f"  {attr_name}: {variable.getncattr(attr_name)}")
        print("\n")
    else:
        # Briefly list variables that are not obviously time-related
        print(f"Other Variable: {var_name} (inspect manually if needed)")

# Close the dataset
dataset.close()
