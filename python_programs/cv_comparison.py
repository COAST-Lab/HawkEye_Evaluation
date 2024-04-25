import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import warnings

# Setup directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'statistics', 'comprehensive_stats.csv')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'statistics', 'visual_analysis')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

warnings.filterwarnings('ignore', category=UserWarning)

# Configuration
pixel_window_size = '1x1'

print("Loading data...")
data = pd.read_csv(DATA_DIR)
print("Data loaded successfully.")

# Filter data
data = data[data['Pixel_Window_Size'] == pixel_window_size]

# Order categories
depth_order = ['0-10m']
data['Depth_Range'] = pd.Categorical(data['Depth_Range'], categories=depth_order, ordered=True)
data.sort_values(['Sensor_Name', 'Depth_Range'], inplace=True)

# Reshape data to make 'CV_true' and 'CV_predicted' comparable in the same plot
data_melted = data.melt(id_vars=['Sensor_Name', 'Depth_Range'], value_vars=['CV_true', 'CV_predicted'], var_name='Metric', value_name='Value')

print("Generating plot...")
plt.figure(figsize=(16, 8))
sns.barplot(x='Sensor_Name', y='Value', hue='Metric', data=data_melted)
plt.title(f'Comparison of CV True and CV Predicted by Satellite Sensor and Depth Range, {pixel_window_size} Pixel Window Size')
plt.xticks(rotation=45, ha='right')
plt.xlabel('Sensor')
plt.ylabel('Coefficient of Variation')
plt.axhline(0, color='gray', linestyle='solid')
plt.legend(title='Metric')
output_filename = 'cv_true_vs_predicted_comparison.png'
plt.savefig(os.path.join(OUTPUT_DIR, output_filename))
plt.close()

print("Plot generated successfully.")
