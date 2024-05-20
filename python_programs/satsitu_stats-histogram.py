import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'aggregated_satsitu_data_l2.csv')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'statistics', 'histograms')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
warnings.filterwarnings('ignore', category=FutureWarning)

df = pd.read_csv(DATA_DIR)
print("Data loaded successfully.")

title_font_size = 18
axis_label_font_size = 16
tick_label_font_size = 26
legend_font_size = 14

# Dictionary mapping sensor names to identifiers
sensor_datetime_dict = {
    'Hawkeye': ('SEAHAWK1_HAWKEYE', '20230507T150955'),
    'Modisa': ('AQUA_MODIS', '20230507T184501'),
    'S3B': ('S3B_OLCI_EFRNT', '20230507T145511'),
    'S3A': ('S3A_OLCI_EFRNT', '20230507T153421')
}

pixel_window_sizes = ['1x1'] # '2x2', '3x3'

depth_ranges = [(0, 4), (4, 7), (7, 10), (0, 10)]

# Initialize a DataFrame to collect comprehensive statistics
columns = ['Sensor_Name', 'Sensor_File', 'Depth_Range', 'Pixel_Window_Size', 'RMSE', 'MAPE (%)', 'Bias', 'R-squared', 'CV_true', 'CV_predicted']
comprehensive_stats_df = pd.DataFrame(columns=columns)
print("Dataframe for storing results initialized.")

# Loop through each combination of parameters
for sensor_name, (sensor_identifier, date) in sensor_datetime_dict.items():
    for pixel_size in pixel_window_sizes:
        print(f"Processing {sensor_name}, DateTime: {date}, Pixel Size: {pixel_size}")
        sensor_file_pattern = f"{sensor_identifier}.{date}.L2.OC{'.x' if 'OLCI_EFRNT' in sensor_identifier or 'MODIS' in sensor_identifier else ''}"

        for depth_range in depth_ranges:
            depth_range_str = f"{depth_range[0]}-{depth_range[1]}m"
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
            comprehensive_stats_df = pd.concat([comprehensive_stats_df, new_row], ignore_index=True)

            f, ax = plt.subplots(figsize=(10, 6))
            f.set_facecolor('#FFFFFF')  # Set the background color of the figure
            ax.set_facecolor('#EAEAF2')  # Set the background color of the axes

            sns.scatterplot(x=true_values, y=predicted_values, alpha=0.7, s=50, color=".15", ax=ax)
            hist = sns.histplot(x=true_values, y=predicted_values, bins=50, pthresh=.1, cmap="mako", ax=ax, cbar=True)
            sns.kdeplot(x=true_values, y=predicted_values, levels=5, color="w", linewidths=1, ax=ax)

            # Regression model
            sorted_zip = sorted(zip(true_values, predicted_chl_poly), key=lambda x: x[0])
            true_values_sorted, predicted_chl_poly_sorted = zip(*sorted_zip)
            sns.lineplot(x=true_values_sorted, y=predicted_chl_poly_sorted, color='#F76B34', linewidth=2, ax=ax)

            # Adding annotations for the metrics
            ax.annotate(f'RMSE: {rmse:.2f}\nMAPE: {mape:.2f}%\nBias: {bias_value:.2f}\nR²: {r_squared_poly:.2f}',
                        xy=(0.97, 0.95), xycoords='axes fraction',
                        horizontalalignment='right', verticalalignment='top',
                        bbox=dict(boxstyle='round,pad=0.5', fc='#FFFFFF', alpha=0.5))

            #ax.set_xlabel('In Situ Chlorophyll (µg/L)', fontsize=axis_label_font_size)
            #ax.set_ylabel(f'{sensor_name.title()} Chlorophyll (µg/L)', fontsize=axis_label_font_size)
            #ax.set_title(f'{sensor_name.title()}, {date}, {pixel_size}, {depth_range_str}m', fontsize=title_font_size)
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.tick_params(axis='both', which='major', labelsize=tick_label_font_size)

            plot_filename = os.path.join(OUTPUT_DIR, f"{sensor_name}_{date}_{depth_range_str}_{pixel_size}.png")
            plt.savefig(plot_filename, dpi=500, bbox_inches='tight')
            plt.close(f)

print("All processing complete. Saving results...")
comprehensive_csv_filename = os.path.join(OUTPUT_DIR, 'comprehensive_stats.csv')
comprehensive_stats_df.to_csv(comprehensive_csv_filename, index=False)
print("Results saved successfully.")

