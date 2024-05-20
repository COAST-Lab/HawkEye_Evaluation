import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
import os

# Set font sizes
title_font_size = 18
axis_label_font_size = 16
tick_label_font_size = 14
legend_font_size = 14
legend_title_font_size = 14

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'statistics', 'comprehensive_stats.csv')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'statistics', 'visual_analysis')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

warnings.filterwarnings('ignore', category=UserWarning)

pixel_window_size = '1x1'  # Can be changed to '2x2' or '3x3'

print("Loading data...")
data = pd.read_csv(DATA_DIR)
print("Data loaded successfully.")

# Filter data based on pixel window size
data = data[data['Pixel_Window_Size'] == pixel_window_size]

depth_order = ['0-4m', '4-7m', '7-10m', '0-10m']
data['Depth_Range'] = pd.Categorical(data['Depth_Range'], categories=depth_order, ordered=True)

data.sort_values(['Sensor_Name', 'Depth_Range'], inplace=True)

metrics = ['RMSE', 'Bias', 'R-squared', 'MAPE (%)', 'CV_true', 'CV_predicted']

# Loop through each metric and generate a plot
print("Generating plots...")
for metric in metrics:
    print(f"Generating plot for {metric}...")
    plt.figure(figsize=(12, 8))
    plot = sns.barplot(x='Sensor_Name', y=metric, hue='Depth_Range', data=data)
    plot.set_title(f'{metric} for Satellite Sensor by Depth Range, {pixel_window_size} Pixel Window Size', fontsize=title_font_size)
    plot.set_xticklabels(data['Sensor_Name'].unique(), rotation=0, ha='right', fontsize=tick_label_font_size)
    plot.set_yticklabels(plot.get_yticks(), fontsize=tick_label_font_size)
    plt.xlabel('Sensor', fontsize=axis_label_font_size)
    plt.ylabel(metric, fontsize=axis_label_font_size)
    plt.axhline(0, color='gray', linestyle='solid')
    handles, labels = plot.get_legend_handles_labels()
    if labels:
        plt.legend(handles, labels, title='Depth Range of In-Situ Data', title_fontsize=legend_title_font_size, fontsize=legend_font_size)
    output_filename = f'{metric.lower()}_comparison_{pixel_window_size}.png'
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    plt.savefig(output_path, dpi=500, bbox_inches='tight')
    plt.close()
