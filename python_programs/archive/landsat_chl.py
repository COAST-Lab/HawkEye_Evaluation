from netCDF4 import Dataset
import numpy as np

def read_chlor_a_landsat(file_path):
    try:
        with Dataset(file_path, 'r') as nc:
            print("Available variables:", list(nc.groups['geophysical_data'].variables.keys()))
            chlor_a = nc.groups['geophysical_data'].variables['chlor_a-mean'][:]
            print("Raw data sample (before processing):", chlor_a[:5, :5])
            
            # Mask out the fill values
            chlor_a = np.ma.masked_values(chlor_a, -32767)
            if np.ma.is_masked(chlor_a):
                print("Mask was applied. Number of masked elements:", np.sum(chlor_a.mask))
                chlor_a = np.where(chlor_a.mask, np.nan, chlor_a)
            else:
                print("No mask applied. Data might not contain fill values.")
            
            return chlor_a
    except KeyError as e:
        print(f"KeyError: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
file_path = '/Users/mitchtork/Thesis/data/sat_default/landsat/l1a-l3/daily/30m-chlor_a/mean/LANDSAT8_OLI.2023050320230503.DLY.chlor_a.map.nc'
chlor_a_data = read_chlor_a_landsat(file_path)
print("Processed data sample:", chlor_a_data[:5, :5])
