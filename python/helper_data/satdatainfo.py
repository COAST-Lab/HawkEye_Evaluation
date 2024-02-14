import netCDF4 as nc

# Open the NetCDF file
ds = nc.Dataset('/Users/mitchtork/HawkEye_Evaluation/data/satellite_matchups/locations/masonboro/s3b/daily/chlor_a/mean/S3B_OLCI_EFR.2023050620230506.chlor_a-mean.smi.nc')

# Access the chlor_a variable
chlor_a_var = ds.variables['chlor_a']

# Get the data type of the variable
data_type = chlor_a_var.dtype

# Get the shape of the data array
shape = chlor_a_var.shape

print(f'Data Type: {data_type}')
print(f'Shape: {shape}')
