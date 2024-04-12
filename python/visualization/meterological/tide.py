import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# Load the dataset
file_path = '/Users/mitchtork/HawkEye_Evaluation/data/meterological/tide/CO-OPS_8658163_met_wb.csv'
tide_data = pd.read_csv(file_path)

# Combine Date and Time columns and convert to datetime
tide_data['DateTime'] = pd.to_datetime(tide_data['Date'] + ' ' + tide_data['Time (GMT)'])

# Set the DateTime as the index of the dataframe
tide_data.set_index('DateTime', inplace=True)

# Plotting
fig, ax = plt.subplots(figsize=(15, 7))  # Increase figure size for better label space
ax.plot(tide_data.index, tide_data['Verified (m)'], label='Tide Level (m)', color='#1f77b4')  # Blue color
ax.set_xlabel('Date, Time')
ax.set_ylabel('Height in meters (MLLW)')
ax.set_title('Tide Levels at Wrightsville Beach')
ax.grid(True)

# Set the background color
fig.patch.set_facecolor('#FAFAFA')  # Set the figure's background color
ax.set_facecolor('#FAFAFA')  # Set the axes' background color

# Set x-axis to show date and time in 6-hour intervals
ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

# Set x-axis limits
start_date = pd.to_datetime('2023-05-03 12:00')
end_date = pd.to_datetime('2023-05-08 12:00')
ax.set_xlim(start_date, end_date)

# Highlight in-situ sampling window
in_situ_start = pd.to_datetime('2023-05-05 10:00')
in_situ_end = pd.to_datetime('2023-05-05 14:00')
ax.axvspan(in_situ_start, in_situ_end, color='#2ca02c', alpha=0.3, label='In-situ Sampling') # Green color

# Group satellite data acquisition times
group1_time = pd.to_datetime('2023-05-03 15:45')
group2_time = pd.to_datetime('2023-05-06 15:00')
group3_time = pd.to_datetime('2023-05-07 15:00')
group4_time = pd.to_datetime('2023-05-07 18:45')

# Group 1: Landsat 8 OLI (May 3) - Pink, solid line
ax.axvline(x=group1_time, color='#e377c2', linestyle='-', label='Satellite Group 1 (OLI8 - May 3)')

# Group 2: HawkEye, OLCI (May 6) - Orange, long dash pattern
ax.axvline(x=group2_time, color='#ff7f0e', linestyle=(0, (5, 10)), label='Satellite Group 2 (HawkEye, OLCI - May 6)')

# Group 3: HawkEye, OLCI x2 (May 7) - Purple, dotted line
ax.axvline(x=group3_time, color='#9467bd', linestyle=':', label='Satellite Group 3 (HawkEye, OLCI x2 - May 7)')

# Group 4: MODIS (May 7) - Brown, dot-dashed line
ax.axvline(x=group4_time, color='#8c564b', linestyle='-.', label='Satellite Group 4 (MODIS - May 7)')

# Adjust the legend and plot layout
ax.legend(loc='upper left', bbox_to_anchor=(1, 1), facecolor='#FAFAFA') 

# Improve x-axis date labels to prevent overlap
fig.autofmt_xdate()  # Auto-format date labels
plt.tight_layout(rect=[0, 0.1, 1, 1])  # Adjust layout to make room for x-axis labels

# Save the plot as a PNG file in the specified directory
save_path = '/Users/mitchtork/HawkEye_Evaluation/visualization/meterological/wb_tides.png'
os.makedirs(os.path.dirname(save_path), exist_ok=True)
plt.savefig(save_path, bbox_inches='tight', facecolor=fig.get_facecolor())  # Ensure the saved figure retains the background color

# Display the plot
plt.show()