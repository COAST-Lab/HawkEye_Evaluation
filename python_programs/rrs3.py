import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from scipy.optimize import curve_fit
from scipy.interpolate import griddata

# Define directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INSITU_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'satsitu_l2.csv')
SAT_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satellite')
VISUAL_SAVE_DIR = os.path.join(SCRIPT_DIR, '..', 'visualization', 'satsitu', 'mbr')

# Create visualization directory if it does not exist
if not os.path.exists(VISUAL_SAVE_DIR):
    os.makedirs(VISUAL_SAVE_DIR)

# Function to load Rrs data from NetCDF files
def load_rrs(file_path, var_name):
    with Dataset(file_path, 'r') as nc:
        # Check if the variable exists in the geophysical_data group
        if 'geophysical_data' in nc.groups:
            geophysical_data = nc.groups['geophysical_data']
            if var_name in geophysical_data.variables:
                rrs_data = geophysical_data.variables[var_name][:]
                return rrs_data
            else:
                raise KeyError(f"Variable '{var_name}' not found in the geophysical_data group of the NetCDF file")
        else:
            raise KeyError("Group 'geophysical_data' not found in the NetCDF file")

# Define file paths for each sensor
hawkeye_file = os.path.join(SAT_DIR, 'hawkeye', 'l2', 'SEAHAWK1_HAWKEYE.20230507T150955.L2.OC.nc')
modisa_file = os.path.join(SAT_DIR, 'modisa', 'l2', 'AQUA_MODIS.20230507T184501.L2.OC.x.nc')
s3a_file = os.path.join(SAT_DIR, 's3a', 'l2', 'S3A_OLCI_EFRNT.20230507T153421.L2.OC.x.nc')
s3b_file = os.path.join(SAT_DIR, 's3b', 'l2', 'S3B_OLCI_EFRNT.20230507T145511.L2.OC.x.nc')

# Load in-situ chlorophyll data using a relative path
print(f"Loading in-situ chlorophyll data from {INSITU_DIR}...")
df = pd.read_csv(INSITU_DIR)
print("Data loaded successfully.")

print(df.columns)

# Define sensor datetime and other parameters
sensor_datetime_dict = {
    'HawkEye': ('SEAHAWK1_HAWKEYE', '20230507T150955', hawkeye_file),
    'Modisa': ('AQUA_MODIS', '20230507T184501', modisa_file),
    'S3B': ('S3B_OLCI_EFRNT', '20230507T145511', s3b_file),
    'S3A': ('S3A_OLCI_EFRNT', '20230507T153421', s3a_file)
}
pixel_window_sizes = ['1x1']
depth_ranges = [(0, 10)]

# Load Rrs data for each sensor before the loop
print("Loading Rrs data for each sensor...")
rrs_hawkeye = {band: load_rrs(hawkeye_file, f'Rrs_{band}') for band in ['447', '488', '510', '556']}
rrs_modisa = {band: load_rrs(modisa_file, f'Rrs_{band}') for band in ['412', '443', '488', '555']}
rrs_s3a = {band: load_rrs(s3a_file, f'Rrs_{band}') for band in ['443', '490', '510', '560']}
rrs_s3b = {band: load_rrs(s3b_file, f'Rrs_{band}') for band in ['443', '490', '510', '560']}
print("Rrs data loaded successfully.")

# Directory to save plots
save_dir = VISUAL_SAVE_DIR

# Iterate over sensors and perform analysis
for sensor_name, (sensor_identifier, date, file_path) in sensor_datetime_dict.items():
    for pixel_size in pixel_window_sizes:
        print(f"\nProcessing {sensor_name}, DateTime: {date}, Pixel Size: {pixel_size}")

        for depth_range in depth_ranges:
            depth_range_str = f"{depth_range[0]}-{depth_range[1]}m"
            true_value_col = 'chlor_a'
            predicted_value_col = f'{sensor_identifier}.{date}.L2.OC_chl' if sensor_name == 'HawkEye' else f'{sensor_identifier}.{date}.L2.OC.x_chl'

            # Check if the predicted_value_col exists in the DataFrame
            if predicted_value_col not in df.columns:
                print(f"Column {predicted_value_col} not found in the DataFrame. Available columns: {df.columns}")
                continue

            # Filter out rows with NaN values in the relevant columns
            mask = ~df[true_value_col].isna() & ~df[predicted_value_col].isna()
            true_values = df.loc[mask, true_value_col].values
            lat_values = df.loc[mask, 'lat'].values
            lon_values = df.loc[mask, 'lon'].values

            # Choose the appropriate Rrs data for the current sensor
            if sensor_name == 'HawkEye':
                rrs = rrs_hawkeye
                bands = ['447', '488', '510', '556']
            elif sensor_name == 'Modisa':
                rrs = rrs_modisa
                bands = ['412', '443', '488', '555']
            elif sensor_name == 'S3A':
                rrs = rrs_s3a
                bands = ['443', '490', '510', '560']
            elif sensor_name == 'S3B':
                rrs = rrs_s3b
                bands = ['443', '490', '510', '560']

            # Create lat/lon meshgrid for satellite data
            first_band = bands[0]
            sat_lat = np.linspace(np.min(lat_values), np.max(lat_values), rrs[first_band].shape[0])
            sat_lon = np.linspace(np.min(lon_values), np.max(lon_values), rrs[first_band].shape[1])
            sat_lon, sat_lat = np.meshgrid(sat_lon, sat_lat)

            # Interpolate Rrs data to match in-situ data points
            rrs_interp = {band: griddata((sat_lat.flatten(), sat_lon.flatten()), data.flatten(), (lat_values, lon_values), method='nearest') for band, data in rrs.items()}

            # Calculate MBR
            if sensor_name == 'Modisa':
                X = np.log10(np.maximum.reduce([rrs_interp['412'], rrs_interp['443'], rrs_interp['488']]) / rrs_interp['555'])
            else:
                X = np.log10(np.maximum.reduce([rrs_interp[bands[0]], rrs_interp[bands[1]], rrs_interp[bands[2]]]) / rrs_interp[bands[3]])

            # Remove NaNs and Infs
            valid_mask = np.isfinite(X) & np.isfinite(true_values)
            X = X[valid_mask]
            true_values = true_values[valid_mask]

            # Check and remove any non-positive values in true_values and X
            non_positive_mask = (true_values > 0) & (X > 0)
            X = X[non_positive_mask]
            true_values = true_values[non_positive_mask]

            # N is the number of valid data points after cleaning
            N = X.size

            # Print the size of X and true_values after cleaning
            print(f"Number of valid data points for {sensor_name} after cleaning: {N}")

            # Fit a fourth-order polynomial curve to recalculate coefficients
            def poly4(x, a0, a1, a2, a3, a4):
                return a0 + a1*x + a2*x**2 + a3*x**3 + a4*x**4

            # Polynomial fitting to the data
            popt, _ = curve_fit(poly4, X, np.log10(true_values))
            a0, a1, a2, a3, a4 = popt
            print(f"Recalculated coefficients for {sensor_name}: {popt}")

            # Calculate estimated CHL based on MBR
            log_chl_est = a0 + a1*X + a2*X + a3*X**3 + a4*X**4
            chl_est = 10**log_chl_est

            # Scatter plot of MBR vs in-situ CHL with smaller data points
            plt.scatter(X, true_values, color='blue', label='Data Points', s=10)

            # Fit a fourth-order polynomial curve to plot
            x_fit = np.linspace(min(X), max(X), 100)
            y_fit = poly4(x_fit, *popt)

            # Convert fitted log values back to normal scale
            plt.plot(x_fit, 10**y_fit, color='red', label='Polynomial Fit')

            # Add labels and title
            plt.xlabel('MBR')
            plt.ylabel('In-situ Chlorophyll-a (mg/m^3)')
            plt.title(f'MBR vs In-situ Chlorophyll-a for {sensor_name} on {date}')
            plt.legend()

            # Save the plot
            plot_filename = f'{sensor_name}_{date}_{pixel_size}_{depth_range_str}.png'
            plot_filepath = os.path.join(save_dir, plot_filename)
            plt.savefig(plot_filepath)
            plt.close()
            print(f"Saving plot to {plot_filepath}...")

print("All results saved successfully.")
