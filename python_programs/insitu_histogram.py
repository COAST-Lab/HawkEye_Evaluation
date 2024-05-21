import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'satsitu', 'statistics', 'histograms')
comprehensive_stats_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'comprehensive_stats.csv'))

for _, row in comprehensive_stats_df.iterrows():
    true_values = pd.Series(row['True_Values'])
    predicted_values = pd.Series(row['Predicted_Values'])
    sensor_name = row['Sensor_Name']
    depth_range_str = row['Depth_Range']
    pixel_size = row['Pixel_Window_Size']
    date = row['Sensor_File'].split('.')[1]

    f, ax = plt.subplots(figsize=(10, 6))
    f.set_facecolor('#FFFFFF')
    ax.set_facecolor('#EAEAF2')

    sns.scatterplot(x=true_values, y=predicted_values, alpha=0.7, s=50, color=".15", ax=ax)
    sns.histplot(x=true_values, y=predicted_values, bins=50, pthresh=.1, cmap="mako", ax=ax, cbar=True)
    sns.kdeplot(x=true_values, y=predicted_values, levels=5, color="w", linewidths=1, ax=ax)
    sns.lineplot(x=true_values, y=row['Predicted_Polynomial'], color='#F76B34', linewidth=2, ax=ax)

    ax.annotate(f'RMSE: {row["RMSE"]:.2f}\nMAPE: {row["MAPE (%)"]:.2f}%\nBias: {row["Bias"]:.2f}\nR²: {row["R-squared"]:.2f}',
                xy=(0.97, 0.95), xycoords='axes fraction', horizontalalignment='right', verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', fc='#FFFFFF', alpha=0.5))

    ax.set_xlabel('In Situ Chlorophyll (µg/L)', fontsize=16)
    ax.set_ylabel(f'{sensor_name} Chlorophyll (µg/L)', fontsize=16)
    ax.set_title(f'{sensor_name}, {date}, {pixel_size}, {depth_range_str}', fontsize=18)
    ax.tick_params(axis='both', which='major', labelsize=14)

    plot_filename = os.path.join(OUTPUT_DIR, f"{sensor_name}_{date}_{depth_range_str}_{pixel_size}.png")
    plt.savefig(plot_filename, dpi=500, bbox_inches='tight')
    plt.close(f)

print("All plots generated successfully.")
