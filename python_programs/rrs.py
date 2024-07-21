import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Load the merged dataset
data_path = '/Users/mitchtork/Thesis/data/satsitu/satsitu_l2_rrs.csv'
data = pd.read_csv(data_path)

# Function to calculate MBR using OC4
def calculate_oc4_mbr(row, rrs_bands, rrs_green):
    try:
        rrs_values = [row[band] for band in rrs_bands if pd.notna(row[band])]
        if not rrs_values:
            return np.nan
        max_rrs = np.max(rrs_values)
        green_rrs = row[rrs_green]
        if pd.notna(max_rrs) and pd.notna(green_rrs) and green_rrs != 0:
            return np.log10(max_rrs / green_rrs)
        else:
            return np.nan
    except KeyError as e:
        print(f"KeyError: {e}")
        return np.nan

# Define Rrs bands for each sensor
rrs_bands_dict = {
    'hawkeye': {'blue': ['SEAHAWK1_HAWKEYE.20230507T150955.L2.OC_Rrs_447', 'SEAHAWK1_HAWKEYE.20230507T150955.L2.OC_Rrs_488', 'SEAHAWK1_HAWKEYE.20230507T150955.L2.OC_Rrs_510'], 'green': 'SEAHAWK1_HAWKEYE.20230507T150955.L2.OC_Rrs_556'},
    'modisa': {'blue': ['AQUA_MODIS.20230507T184501.L2.OC.x_Rrs_412', 'AQUA_MODIS.20230507T184501.L2.OC.x_Rrs_443', 'AQUA_MODIS.20230507T184501.L2.OC.x_Rrs_488'], 'green': 'AQUA_MODIS.20230507T184501.L2.OC.x_Rrs_555'},
    's3b': {'blue': ['S3B_OLCI_EFRNT.20230507T145511.L2.OC.x_Rrs_443', 'S3B_OLCI_EFRNT.20230507T145511.L2.OC.x_Rrs_490', 'S3B_OLCI_EFRNT.20230507T145511.L2.OC.x_Rrs_510'], 'green': 'S3B_OLCI_EFRNT.20230507T145511.L2.OC.x_Rrs_560'},
    's3a': {'blue': ['S3A_OLCI_EFRNT.20230507T153421.L2.OC.x_Rrs_443', 'S3A_OLCI_EFRNT.20230507T153421.L2.OC.x_Rrs_490', 'S3A_OLCI_EFRNT.20230507T153421.L2.OC.x_Rrs_510'], 'green': 'S3A_OLCI_EFRNT.20230507T153421.L2.OC.x_Rrs_560'}
}

# Calculate MBR for each sensor
for sensor, bands in rrs_bands_dict.items():
    mbr_col = f'{sensor}_MBR'
    data[mbr_col] = data.apply(lambda row: calculate_oc4_mbr(row, bands['blue'], bands['green']), axis=1)

# Function to create scatter plot
def create_scatter_plot(sensor):
    plt.figure(figsize=(10, 6))
    plt.scatter(data[f'{sensor}_MBR'], data['chlor_a'], color='blue', label='Data Points')
    plt.xlabel(f'{sensor} Log10(MBR)')
    plt.ylabel('In Situ Chlorophyll-a')
    plt.title(f'{sensor} Log10(MBR) vs In Situ Chlorophyll-a')

    # Linear regression
    valid_data = data[[f'{sensor}_MBR', 'chlor_a']].dropna()
    X = valid_data[f'{sensor}_MBR'].values.reshape(-1, 1)
    y = valid_data['chlor_a'].values
    reg = LinearRegression().fit(X, y)
    y_pred = reg.predict(X)
    plt.plot(X, y_pred, color='red', linestyle='--', label=f'Linear fit (R²={r2_score(y, y_pred):.3f})')

    plt.legend()
    plt.grid(True)
    plt.show()

# Create scatter plots for each sensor
for sensor in rrs_bands_dict.keys():
    create_scatter_plot(sensor)
