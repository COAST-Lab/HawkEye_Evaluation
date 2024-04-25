import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'statistics', 'comprehensive_stats.csv')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'statistics', 'visual_analysis')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

warnings.filterwarnings('ignore', category=UserWarning)

print("Loading data...")
data = pd.read_csv(DATA_DIR)
print("Data loaded successfully.")

depth_order = ['0-10m']
data['Depth_Range'] = pd.Categorical(data['Depth_Range'], categories=depth_order, ordered=True)

data.sort_values(['Sensor_Name', 'Depth_Range'], inplace=True)

metrics = ['RMSE', 'Bias', 'R-squared', 'MAPE (%)', 'CV_true', 'CV_predicted']

# Loop through each metric and generate a comparative plot
print("Generating plots...")
for metric in metrics:
    print(f"Generating plot for {metric}...")
    plt.figure(figsize=(12, 8))
    plot = sns.barplot(x='Sensor_Name', y=metric, hue='Pixel_Window_Size', data=data)
    plot.set_title(f'Comparison of {metric} Across Pixel Window Sizes by Sensor, 7 May 2023')
    plot.set_xticklabels(data['Sensor_Name'].unique(), rotation=45, ha='right')
    plt.xlabel('Sensor')
    plt.ylabel(metric)
    plt.axhline(0, color='gray', linestyle='solid')
    handles, labels = plot.get_legend_handles_labels()
    if labels:
        plt.legend(handles, labels, title='Pixel Window Size')
    output_filename = f'{metric.lower()}_size_comparison.png'
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    plt.savefig(output_path)
    plt.close()

print("Plots generated successfully.")
