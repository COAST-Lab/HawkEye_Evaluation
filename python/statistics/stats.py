import pandas as pd
import numpy as np
import os
from scipy import stats
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
import operator

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', '..', 'data', 'satsitu', 'combined_aggregated_satsitu_data_l2.csv')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', '..', '..', 'data', 'satsitu', 'statistics', 'l2')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Load the dataset
df = pd.read_csv(DATA_DIR)

# User-defined inputs
sensor_name = 'hawkeye' # Options: 'hawkeye', 'modisa', 's3b', 's3a'
satellite_capture_date = '20230507T150955' # see "sensor_name_dict"
pixel_window_size = '1x1' # Options: '1x1', '2x2', '3x3'

#SEAHAWK1_HAWKEYE.20230506T150841.L2.OC
#SEAHAWK1_HAWKEYE.20230507T150955.L2.OC
#AQUA_MODIS.20230507T184501.L2.OC.x
#S3A_OLCI_EFRNT.20230503T153806.L2.OC.x
#S3A_OLCI_EFRNT.20230504T151155.L2.OC.x
#S3A_OLCI_EFRNT.20230507T153421.L2.OC.x
#S3B_OLCI_EFRNT.20230503T145856.L2.OC.x
#S3B_OLCI_EFRNT.20230506T152122.L2.OC.x
#S3B_OLCI_EFRNT.20230507T145511.L2.OC.x

# Dictionary mapping simple sensor names to their dataset identifiers
sensor_name_dict = {
    'hawkeye': 'SEAHAWK1_HAWKEYE',
    'modisa': 'AQUA_MODIS',
    's3b': 'S3B_OLCI_EFRNT',
    's3a': 'S3A_OLCI_EFRNT'
}

def build_satellite_pattern(sensor_identifier, capture_date):
    # Add the .x suffix if the sensor identifier indicates it's required
    suffix = '.x' if 'OLCI_EFRNT' in sensor_identifier or 'MODIS' in sensor_identifier else ''
    return f"{sensor_identifier}.{capture_date}.L2.OC{suffix}"

# Convert sensor_name to the full satellite identifier using the dictionary
full_sensor_name = sensor_name_dict[sensor_name]
sensor_file_pattern = build_satellite_pattern(full_sensor_name, satellite_capture_date)

depth_ranges = [(0, 3), (4, 6), (7, 10), (0, 10), (0, 5), (5, 10)]

# Initialize a DataFrame to collect comprehensive statistics
columns = ['Sensor File', 'Depth Range', 'Pixel Window Size', 'RMSE', 'MAPE', 'Bias', 'R-squared']
comprehensive_stats_df = pd.DataFrame(columns=columns)

for depth_range in depth_ranges:
    depth_range_str = f"{depth_range[0]}-{depth_range[1]}m"
    true_value_col = f'{sensor_file_pattern}_insitu_chl_{depth_range_str}_{pixel_window_size}'
    predicted_value_col = f'{sensor_file_pattern}_chl_{pixel_window_size}'
    
    if true_value_col not in df.columns or predicted_value_col not in df.columns:
        print(f"Missing columns: {true_value_col} or {predicted_value_col}")
        continue

    mask = ~df[true_value_col].isna() & ~df[predicted_value_col].isna()
    true_values = df.loc[mask, true_value_col]
    predicted_values = df.loc[mask, predicted_value_col]

    rmse = np.sqrt(mean_squared_error(true_values, predicted_values))
    mape = np.mean(np.abs((true_values - predicted_values) / true_values)) * 100
    bias_value = np.mean(predicted_values - true_values)

    polyreg = make_pipeline(PolynomialFeatures(1), LinearRegression())
    polyreg.fit(true_values.values.reshape(-1, 1), predicted_values.values)

    predicted_chl_poly = polyreg.predict(true_values.values.reshape(-1, 1))
    r_squared_poly = r2_score(predicted_values, predicted_chl_poly)

    # Append the statistics for the current iteration to the DataFrame
    comprehensive_stats_df = comprehensive_stats_df._append({
        'Sensor File': sensor_file_pattern,
        'Depth Range': depth_range_str,
        'Pixel Window Size': pixel_window_size,
        'RMSE': rmse,
        'MAPE (%)': mape,
        'Bias': bias_value,
        'R-squared': r_squared_poly
    }, ignore_index=True)

    # Define custom labels based on user-defined inputs and calculated metrics
    x_label = f'In situ chlorophyll (µg/L), Depth: {depth_range_str}'
    y_label = f'{sensor_name.title()} chlorophyll (µg/L)'  # Capitalizes the first letter of sensor_name
    plot_title = f'{sensor_name.title()}, {satellite_capture_date}, {pixel_window_size}'

    # Plotting adjustments
    plt.figure(figsize=(10, 6), facecolor='#FAFAFA')
    sns.scatterplot(x=true_values, y=predicted_values, alpha=0.7)

    # Generate a line for the polynomial regression model
    sorted_zip = sorted(zip(true_values, predicted_chl_poly), key=lambda x: x[0])
    true_values_sorted, predicted_chl_poly_sorted = zip(*sorted_zip)

    # Plot the regression line
    plt.plot(true_values_sorted, predicted_chl_poly_sorted, color='#F76B34', linewidth=2)

    # Adding annotations for the metrics
    plt.annotate(f'RMSE: {rmse:.2f}\nMAPE: {mape:.2f}%\nBias: {bias_value:.2f}\nR²: {r_squared_poly:.2f}',
                xy=(0.97, 0.95), xycoords='axes fraction',
                horizontalalignment='right', verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', fc='#F76B34', alpha=0.5))

    # Setting the x-axis and y-axis labels
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    # Setting the plot title
    plt.title(plot_title)

    # Saving the plot with a filename that reflects the sensor name, satellite capture date, depth range, and pixel window size
    plot_filename = os.path.join(OUTPUT_DIR, f"{sensor_name}_{satellite_capture_date}_{depth_range_str}_{pixel_window_size}.png")
    plt.savefig(plot_filename, bbox_inches='tight')
    plt.close() 

# Specify filename for the CSV summary
csv_filename = os.path.join(OUTPUT_DIR, f"stats_{sensor_name}_{satellite_capture_date}_{pixel_window_size}.csv")

# Export DataFrame to CSV
comprehensive_stats_df.to_csv(csv_filename, index=False)
