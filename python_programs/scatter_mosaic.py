import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt
import warnings

# Define directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'aggregated_satsitu_data_l2.csv')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'statistics')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
warnings.filterwarnings('ignore', category=FutureWarning)

# Load the dataset
df = pd.read_csv(DATA_DIR)
print("Data loaded successfully.")

# Dictionary mapping sensor names to identifiers and their specific column pattern for chlorophyll
sensor_datetime_dict = {
    'Hawkeye': 'SEAHAWK1_HAWKEYE.20230507T150955.L2.OC',
    'Modisa': 'AQUA_MODIS.20230507T184501.L2.OC',
    'S3B': 'S3B_OLCI_EFRNT.20230507T145511.L2.OC',
    'S3A': 'S3A_OLCI_EFRNT.20230507T153421.L2.OC'
}

depth_ranges = ['0-4', '4-7', '7-10', '0-10']

# Gather all relevant columns for plotting
plot_data = pd.DataFrame()
for sensor_name, sensor_code in sensor_datetime_dict.items():
    for depth_range in depth_ranges:
        true_value_col = f"{sensor_code}.x_insitu_chl_{depth_range}_1x1"
        predicted_value_col = f"{sensor_code}.x_chl_1x1"

        # Check if columns exist
        if true_value_col in df.columns and predicted_value_col in df.columns:
            temp_df = df[[true_value_col, predicted_value_col]].dropna()
            temp_df['Sensor'] = sensor_name
            temp_df['Depth Range'] = depth_range
            plot_data = pd.concat([plot_data, temp_df], ignore_index=True)
        else:
            print(f"Columns {true_value_col} and/or {predicted_value_col} not found in data.")


if not plot_data.empty:
    plot_data.columns = ['True Values', 'Predicted Values', 'Sensor', 'Depth Range']

    # Create the FacetGrid
    g = sns.FacetGrid(plot_data, col="Depth Range", row="Sensor", margin_titles=True, height=4)
    g.map_dataframe(sns.scatterplot, x='True Values', y='Predicted Values')
    g.add_legend()
    g.set_axis_labels("In Situ Chlorophyll (µg/L)", "Predicted Chlorophyll (µg/L)")
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle('Scatter Plots by Sensor and Depth Range', fontsize=16)

    # Save the comprehensive plot
    plot_filename = os.path.join(OUTPUT_DIR, 'comprehensive_scatter_plot.png')
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    plt.close()
    print("Plot saved successfully.")
else:
    print("No data available to plot.")
