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
        group = nc.groups['Mapped_Data_and_Params']
        if var_name in group.variables:
            rrs_data = group.variables[var_name][:]
            return rrs_data
        else:
            raise KeyError(f"Variable '{var_name}' not found in the NetCDF file")

# Define relative file paths for each sensor
hawkeye_files = {
    '447': os.path.join(SAT_DIR, 'hawkeye', 'l2-l3', 'daily', '75m-Rrs_447', 'mean', 'SEAHAWK1_HAWKEYE.2023050720230507.DLY.Rrs_447.map.nc'),
    '488': os.path.join(SAT_DIR, 'hawkeye', 'l2-l3', 'daily', '75m-Rrs_488', 'mean', 'SEAHAWK1_HAWKEYE.2023050720230507.DLY.Rrs_488.map.nc'),
    '510': os.path.join(SAT_DIR, 'hawkeye', 'l2-l3', 'daily', '75m-Rrs_510', 'mean', 'SEAHAWK1_HAWKEYE.2023050720230507.DLY.Rrs_510.map.nc'),
    '556': os.path.join(SAT_DIR, 'hawkeye', 'l2-l3', 'daily', '75m-Rrs_556', 'mean', 'SEAHAWK1_HAWKEYE.2023050720230507.DLY.Rrs_556.map.nc'),
}

modisa_files = {
    '412': os.path.join(SAT_DIR, 'modisa', 'l2-l3', 'daily', '1000m-Rrs_412', 'mean', 'AQUA_MODIS.2023050720230507.DLY.Rrs_412.map.nc'),
    '443': os.path.join(SAT_DIR, 'modisa', 'l2-l3', 'daily', '1000m-Rrs_443', 'mean', 'AQUA_MODIS.2023050720230507.DLY.Rrs_443.map.nc'),
    '488': os.path.join(SAT_DIR, 'modisa', 'l2-l3', 'daily', '1000m-Rrs_488', 'mean', 'AQUA_MODIS.2023050720230507.DLY.Rrs_488.map.nc'),
    '555': os.path.join(SAT_DIR, 'modisa', 'l2-l3', 'daily', '1000m-Rrs_555', 'mean', 'AQUA_MODIS.2023050720230507.DLY.Rrs_555.map.nc'),
}

s3a_files = {
    '443': os.path.join(SAT_DIR, 's3a', 'l2-l3', 'daily', '300m-Rrs_443', 'mean', 'S3A_OLCI_EFRNT.2023050720230507.DLY.Rrs_443.map.nc'),
    '490': os.path.join(SAT_DIR, 's3a', 'l2-l3', 'daily', '300m-Rrs_490', 'mean', 'S3A_OLCI_EFRNT.2023050720230507.DLY.Rrs_490.map.nc'),
    '510': os.path.join(SAT_DIR, 's3a', 'l2-l3', 'daily', '300m-Rrs_510', 'mean', 'S3A_OLCI_EFRNT.2023050720230507.DLY.Rrs_510.map.nc'),
    '560': os.path.join(SAT_DIR, 's3a', 'l2-l3', 'daily', '300m-Rrs_560', 'mean', 'S3A_OLCI_EFRNT.2023050720230507.DLY.Rrs_560.map.nc'),
}

s3b_files = {
    '443': os.path.join(SAT_DIR, 's3b', 'l2-l3', 'daily', '300m-Rrs_443', 'mean', 'S3B_OLCI_EFRNT.2023050720230507.DLY.Rrs_443.map.nc'),
    '490': os.path.join(SAT_DIR, 's3b', 'l2-l3', 'daily', '300m-Rrs_490', 'mean', 'S3B_OLCI_EFRNT.2023050720230507.DLY.Rrs_490.map.nc'),
    '510': os.path.join(SAT_DIR, 's3b', 'l2-l3', 'daily', '300m-Rrs_510', 'mean', 'S3B_OLCI_EFRNT.2023050720230507.DLY.Rrs_510.map.nc'),
    '560': os.path.join(SAT_DIR, 's3b', 'l2-l3', 'daily', '300m-Rrs_560', 'mean', 'S3B_OLCI_EFRNT.2023050720230507.DLY.Rrs_560.map.nc'),
}

# Load in-situ chlorophyll data using a relative path
print(f"Loading in-situ chlorophyll data from {INSITU_DIR}...")
df = pd.read_csv(INSITU_DIR)
print("Data loaded successfully.")

# Define sensor datetime and other parameters
sensor_datetime_dict = {
    'HawkEye': ('SEAHAWK1_HAWKEYE', '20230507T150955'),
    'Modisa': ('AQUA_MODIS', '20230507T184501'),
    'S3B': ('S3B_OLCI_EFRNT', '20230507T145511'),
    'S3A': ('S3A_OLCI_EFRNT', '20230507T153421')
}
pixel_window_sizes = ['1x1']
depth_ranges = [(0, 10)]

# Load Rrs data for each sensor before the loop
print("Loading Rrs data for each sensor...")
rrs_hawkeye = {band: load_rrs(file, f'Rrs_{band}-mean') for band, file in hawkeye_files.items()}
rrs_modisa = {band: load_rrs(file, f'Rrs_{band}-mean') for band, file in modisa_files.items()}
rrs_s3a = {band: load_rrs(file, f'Rrs_{band}-mean') for band, file in s3a_files.items()}
rrs_s3b = {band: load_rrs(file, f'Rrs_{band}-mean') for band, file in s3b_files.items()}
print("Rrs data loaded successfully.")

# Directory to save plots
save_dir = VISUAL_SAVE_DIR

# Iterate over sensors and perform analysis
for sensor_name, (sensor_identifier, date) in sensor_datetime_dict.items():
    for pixel_size in pixel_window_sizes:
        print(f"\nProcessing {sensor_name}, DateTime: {date}, Pixel Size: {pixel_size}")

        for depth_range in depth_ranges:
            depth_range_str = f"{depth_range[0]}-{depth_range[1]}m"
            true_value_col = 'chlor_a'
            if sensor_name == 'HawkEye':
                predicted_value_col = 'SEAHAWK1_HAWKEYE.20230507T150955.L2.OC_chl'
            elif sensor_name == 'Modisa':
                predicted_value_col = 'AQUA_MODIS.20230507T184501.L2.OC.x_chl'
            elif sensor_name == 'S3A':
                predicted_value_col = 'S3A_OLCI_EFRNT.20230507T153421.L2.OC.x_chl'
            elif sensor_name == 'S3B':
                predicted_value_col = 'S3B_OLCI_EFRNT.20230507T145511.L2.OC.x_chl'

            # Filter out rows with NaN values in the relevant columns
            mask = ~df[true_value_col].isna() & ~df[predicted_value_col].isna()
            true_values = df.loc[mask, true_value_col].values
            lat_values = df.loc[mask, 'lat'].values
            lon_values = df.loc[mask, 'lon'].values

            print(f"Initial data points for {sensor_name}: {len(true_values)}")

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

            # Print min and max values of Rrs bands
            for band in bands:
                print(f"{sensor_name} Rrs {band} min: {np.min(rrs[band])}, max: {np.max(rrs[band])}")

            # Create lat/lon meshgrid for satellite data
            first_band = bands[0]
            sat_lat = np.linspace(np.min(lat_values), np.max(lat_values), rrs[first_band].shape[0])
            sat_lon = np.linspace(np.min(lon_values), np.max(lon_values), rrs[first_band].shape[1])
            sat_lon, sat_lat = np.meshgrid(sat_lon, sat_lat)

            # Interpolate Rrs data to match in-situ data points
            rrs_interp = {band: griddata((sat_lat.flatten(), sat_lon.flatten()), data.flatten(), (lat_values, lon_values), method='nearest') for band, data in rrs.items()}

            # Print some interpolated Rrs values for debugging
            for band in bands:
                print(f"Interpolated {sensor_name} Rrs {band} values: {rrs_interp[band][:10]}")

            # Calculate MBR
            if sensor_name == 'Modisa':
                X = np.log10(np.maximum.reduce([rrs_interp['412'], rrs_interp['443'], rrs_interp['488']]) / rrs_interp['555'])
            else:
                X = np.log10(np.maximum.reduce([rrs_interp[bands[0]], rrs_interp[bands[1]], rrs_interp[bands[2]]]) / rrs_interp[bands[3]])

            # Remove NaNs and Infs
            print(f"Data points before removing NaNs and Infs for {sensor_name}: {len(X)}")
            valid_mask = np.isfinite(X) & np.isfinite(true_values)
            X = X[valid_mask]
            true_values = true_values[valid_mask]
            print(f"Data points after removing NaNs and Infs for {sensor_name}: {len(X)}")

            # Remove zero and negative values before log transformation
            print(f"Checking for non-positive values in X: {np.sum(X <= 0)}")
            print(f"Checking for non-positive values in true_values: {np.sum(true_values <= 0)}")
            valid_mask = (X > 0) & (true_values > 0)
            X = X[valid_mask]
            true_values = true_values[valid_mask]
            print(f"Data points after removing non-positive values for {sensor_name}: {len(X)}")

            # N is the number of valid data points after cleaning
            N = X.size

            # Print the size of X and true_values after cleaning
            print(f"Number of valid data points for {sensor_name} after cleaning: {N}")

            if N == 0:
                print(f"No valid data points for {sensor_name}. Skipping...")
                continue

            # Fit a fourth-order polynomial curve to recalculate coefficients
            def poly4(x, a0, a1, a2, a3, a4):
                return a0 + a1*x + a2*x**2 + a3*x**3 + a4*x**4

            # Polynomial fitting to the data
            popt, _ = curve_fit(poly4, X, np.log10(true_values))
            a0, a1, a2, a3, a4 = popt
            print(f"Recalculated coefficients for {sensor_name}: {popt}")

            # Calculate estimated CHL based on MBR
            log_chl_est = a0 + a1*X + a2*X**2 + a3*X**3 + a4*X**4
            chl_est = 10**log_chl_est

            # Scatter plot of MBR vs in-situ CHL with smaller data points
            plt.scatter(X, true_values, color='blue', label='Data Points', s=10)

            # Fit a fourth-order polynomial curve to plot
            x_fit = np.linspace(min(X), max(X), 100)
            y_fit = poly4(x_fit, *popt)

            # Convert fitted log values back to normal scale
            plt.plot(x_fit, 10**y_fit, color='red', label='Polynomial Fit')

            # Calculate R-squared
            residuals = np.log10(true_values) - poly4(X, *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((np.log10(true_values) - np.mean(np.log10(true_values)))**2)
            r_squared = 1 - (ss_res / ss_tot)

            # Add N and R-squared to the legend
            plt.legend(title=f'{sensor_name}: N = {N}, $R^2$ = {r_squared:.2f}')

            # Annotations
            plt.xlabel('Maximum Band Ratio')
            plt.ylabel('Chlorophyll a (µg/L)')
            plt.title(f'MBR vs In-situ CHL for {sensor_name}')

            # Save plot
            plot_filename = f'{sensor_name}_{date}_{pixel_size}_{depth_range_str}.png'
            print(f"Saving plot to {os.path.join(save_dir, plot_filename)}...")
            plt.savefig(os.path.join(save_dir, plot_filename))
            plt.close()  # Close the plot to free memory

print("All results saved successfully.")
