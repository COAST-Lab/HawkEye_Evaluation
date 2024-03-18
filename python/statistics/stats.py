import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Dynamically calculate the base directory based on the script's location
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths for the dataset and the output directory relative to script_dir
data_dir = os.path.join(script_dir, '../../../data/satsitu/aggregated_data')
output_dir = os.path.join(script_dir, '../../../data/satsitu/statistics/l3')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load the dataset with a relative path
file_path = os.path.join(data_dir, 'master_dataset_l3.csv')
df = pd.read_csv(file_path)

def mean_absolute_percentage_error(y_true, y_pred): 
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    non_zero_mask = y_true != 0
    return np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100

def bias(y_true, y_pred):
    return np.mean(y_pred - y_true)

sensor_name = 'modisa'  # replace with 'modisa', 'hawkeye', 'oli8', 's3a', or 's3b' as needed
pixel_window_size = '1x1'  # replace with '1x1', '2x2', or '3x3' as needed

# Calculate statistics for the chosen pixel window size
true_values = df[f'{sensor_name}_insitu_chl_{pixel_window_size}']
predicted_values = df[f'{sensor_name}_chl_{pixel_window_size}']

# Remove NaN values from the analysis
mask = ~np.isnan(true_values) & ~np.isnan(predicted_values)
true_values, predicted_values = true_values[mask], predicted_values[mask]

# RMSE
rmse = np.sqrt(mean_squared_error(true_values, predicted_values))

# MAPE
mape = mean_absolute_percentage_error(true_values, predicted_values)

# Bias
bias_value = bias(true_values, predicted_values)

# Regression with statsmodels to get the p-value
X_sm = sm.add_constant(true_values.values.reshape(-1, 1))  # Adding a constant for the intercept
model = sm.OLS(predicted_values.values, X_sm).fit()
p_value = model.pvalues[1]  # p-value for the slope coefficient

# You can still calculate predicted values for the line of best fit if needed
predicted_chl_reg = model.predict(X_sm)

# Plotting the results with statistical annotations
plt.figure(figsize=(10, 6), facecolor='#FAFAFA')
sns.scatterplot(x=true_values, y=predicted_values, alpha=0.7)

plt.plot(true_values, predicted_chl_reg, color='#F76B34', linewidth=2)
plt.title(f'Regression and Error Analysis for {sensor_name.capitalize()} ({pixel_window_size} Pixels)')
plt.xlabel('In-Situ Chlorophyll (µg/L)')
plt.ylabel(f'{sensor_name.capitalize()} Chlorophyll (µg/L)')

# Annotations with the statistical metrics
plt.annotate(f'RMSE: {rmse:.2f}\nMAPE: {mape:.2f}%\nBias: {bias_value:.2f}\nP-value: {p_value:.4f}',
             xy=(0.97, 0.95), xycoords='axes fraction',
             horizontalalignment='right', verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.5', fc='#F76B34', alpha=0.5))

# Save the plot to the output directory
plot_filename = os.path.join(output_dir, f'{sensor_name}_{pixel_window_size}_regression_and_error_analysis.png')
plt.savefig(plot_filename, bbox_inches='tight')
plt.close()
