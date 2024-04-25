import xarray as xr

# Load the NetCDF file
ds = xr.open_dataset("/Users/mitchtork/Thesis/data/sat_default/all_l2/SEAHAWK1_HAWKEYE.20230507T150955.L2.OC.nc")

# Print the available data variables to ensure you select the correct ones
print(ds)

# Subset the dataset for the given latitude and longitude range
# Ensure latitude and longitude variables match those in your dataset
subset = ds.sel(latitude=slice(34.10, 34.25), longitude=slice(-77.85, -77.70))

# Print the subset to verify
print(subset)

# Save the subset into a new NetCDF file if needed
subset.to_netcdf("/Users/mitchtork/Thesis/data/sat_default/all_l2/subset_SEAHAWK1_HAWKEYE.20230507T150955.L2.OC.nc")