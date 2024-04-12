from netCDF4 import Dataset

# Example Python code to inspect groups and variables in the dataset
from netCDF4 import Dataset

nc_file = '/Users/mitchtork/Thesis/data/sat_default/landsat/l2/LANDSAT8_OLI.20230503T000000.L2.OC.nc'
with Dataset(nc_file, 'r') as dataset:
    for gname, group in dataset.groups.items():
        print(f"Group: {gname}")
        for var in group.variables:
            print(f"  Variable: {var} - {group.variables[var].dimensions}")
