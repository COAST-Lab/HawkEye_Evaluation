import netCDF4 as nc

# Open the NetCDF file
file_path = '/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/locations/masonboro/s3b/daily/chlor_a/mean/S3B_OLCI_EFR.2023050620230506.chlor_a-mean.smi.nc'
ds = nc.Dataset(file_path)

print(f"File: {file_path}\n")

# Print global attributes
print("Global Attributes:")
for name in ds.ncattrs():
    print(f"{name}: {ds.getncattr(name)}")
print("\n")

# Print dimensions
print("Dimensions:")
for name, dimension in ds.dimensions.items():
    print(f"{name}: size={len(dimension)}")
print("\n")

# Print variables and their details
print("Variables:")
for name, variable in ds.variables.items():
    print(f"{name}:")
    print(f"  data type: {variable.dtype}")
    print(f"  dimensions: {variable.dimensions}")
    print(f"  shape: {variable.shape}")
    for attr_name in variable.ncattrs():
        print(f"  {attr_name}: {variable.getncattr(attr_name)}")
    print("\n")

# Access the chlor_a variable
chlor_a_var = ds.variables['chlor_a']

# Get the data type of the variable
data_type = chlor_a_var.dtype

# Get the shape of the data array
shape = chlor_a_var.shape

print(f"Details for 'chlor_a' Variable:")
print(f"  Data Type: {data_type}")
print(f"  Shape: {shape}")
for attr_name in chlor_a_var.ncattrs():
    print(f"  {attr_name}: {chlor_a_var.getncattr(attr_name)}")

# Close the dataset
ds.close()
