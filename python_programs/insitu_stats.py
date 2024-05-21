import pandas as pd
import numpy as np
import os
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
import warnings

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'aggregated_satsitu_data_l2.csv')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'statistics', 'histograms')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
warnings.filterwarnings('ignore', category=FutureWarning)

df = pd.read_csv(DATA_DIR)
print("Data loaded successfully.")

# Dictionary mapping sensor names to identifiers
sensor_datetime_dict = {
    'Hawkeye': ('SEAHAWK1_HAWKEYE', '20230507T150955'),
    'Modisa': ('AQUA_MODIS', '20230507T184501'),
    'S3B': ('S3B_OLCI_EFRNT', '20230507T145511'),
    'S3A': ('S3A_OLCI_EFRNT', '20230507T153421')
}

pixel_window_sizes = ['1x1']
depth_ranges = [(0, 4), (4, 7), (7, 10), (0, 10)]
columns = ['Sensor_Name', 'Sensor_File', 'Depth_Range', 'Pixel_Window_Size', 'RMSE', 'MAPE (%)', 'Bias', 'R-squared', 'CV_true', 'CV_predicted']
comprehensive_stats_df = pd.DataFrame(columns=columns)
print("Dataframe for storing results initialized.")

for sensor_name, (sensor_identifier, date) in sensor_datetime_dict.items():
    for pixel_size in pixel_window_sizes:
        sensor_file_pattern = f"{sensor_identifier}.{date}.L2.OC{'.x' if 'OLCI_EFRNT' in sensor_identifier or 'MODIS' in sensor_identifier else ''}"
        for depth_range in depth_ranges:
            depth_range_str = f"{depth_range[0]}-{depth_range[1]}m"  # Defining depth_range_str correctly
            true_value_col = f'{sensor_file_pattern}_insitu_chl_{depth_range_str}_{pixel_size}'
            predicted_value_col = f'{sensor_file_pattern}_chl_{pixel_size}'

            if true_value_col not in df.columns or predicted_value_col not in df.columns:
                print(f"Missing columns: {true_value_col} or {predicted_value_col}")
                continue

            mask = ~df[true_value_col].isna() & ~df[predicted_value_col].isna()
            if mask.sum() == 0:
                print(f"No data available for {sensor_name} on {date} with {depth_range_str}")
                continue

            true_values = df.loc[mask, true_value_col]
            predicted_values = df.loc[mask, predicted_value_col]

            rmse = np.sqrt(mean_squared_error(true_values, predicted_values))
            mape = np.mean(np.abs((true_values - predicted_values) / true_values)) * 100
            bias_value = np.mean(predicted_values - true_values)
            cv_true = np.std(true_values) / np.mean(true_values) if np.mean(true_values) != 0 else 0
            cv_predicted = np.std(predicted_values) / np.mean(predicted_values) if np.mean(predicted_values) != 0 else 0

            polyreg = make_pipeline(PolynomialFeatures(1), LinearRegression())
            polyreg.fit(true_values.values.reshape(-1, 1), predicted_values.values)
            predicted_chl_poly = polyreg.predict(true_values.values.reshape(-1, 1))
            r_squared_poly = r2_score(predicted_values, predicted_chl_poly)

            new_row = pd.DataFrame({
                'Sensor_Name': [sensor_name.title()],
                'Sensor_File': [sensor_file_pattern],
                'Depth_Range': [depth_range_str],
                'Pixel_Window_Size': [pixel_size],
                'RMSE': [rmse],
                'MAPE (%)': [mape],
                'Bias': [bias_value],
                'R-squared': [r_squared_poly],
                'CV_true': [cv_true * 100],
                'CV_predicted': [cv_predicted * 100]
            })

            # Use concat instead of append
            comprehensive_stats_df = pd.concat([comprehensive_stats_df, new_row], ignore_index=True)

comprehensive_stats_df.to_csv(os.path.join(OUTPUT_DIR, 'comprehensive_stats.csv'), index=False)
print("Statistics saved successfully.")
