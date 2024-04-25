import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TIDE_DIR = os.path.join(SCRIPT_DIR, 'local_processing_resources', 'meteorological', 'tide', 'CO-OPS_8658163_met_wb.csv')
SAVE_DIR = os.path.join(SCRIPT_DIR, '..', 'visualization', 'meteorological', 'wb_tides.png')
os.makedirs(os.path.dirname(SAVE_DIR), exist_ok=True)

tide_data = pd.read_csv(TIDE_DIR)
tide_data['DateTime'] = pd.to_datetime(tide_data['Date'] + ' ' + tide_data['Time (GMT)'])
tide_data.set_index('DateTime', inplace=True)

daily_change = tide_data['Verified (m)'].resample('D').agg(['max', 'min'])
daily_change['change'] = daily_change['max'] - daily_change['min']
print("Daily Tidal Change:")
print(daily_change['change'])

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(tide_data.index, tide_data['Verified (m)'], label='Tide Level (m)', color='#1f77b4')
ax.set_xlabel('Date, Time', fontsize=14)
ax.set_ylabel('Height in Meters (MLLW)', fontsize=14)
ax.set_title('Tide Levels at Wrightsville Beach', fontsize=16)
ax.grid(True)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

start_date = pd.to_datetime('2023-05-05 06:00')
end_date = pd.to_datetime('2023-05-08 00:00')
ax.set_xlim(start_date, end_date)

in_situ_start = pd.to_datetime('2023-05-05 10:00')
in_situ_end = pd.to_datetime('2023-05-05 15:00')
ax.axvspan(in_situ_start, in_situ_end, color='#2ca02c', alpha=0.3, label='In-situ Sampling')

# Define the times for satellite sensors
seahawk_time = pd.to_datetime('2023-05-07 15:09:55')
sentinel3a_time = pd.to_datetime('2023-05-07 15:34:21')
sentinel3b_time = pd.to_datetime('2023-05-07 14:55:11')
modis_aqua_time = pd.to_datetime('2023-05-07 18:45:01')

ax.axvline(x=seahawk_time, color='purple', linestyle=':', label='SeaHawk/HawkEye')
ax.axvline(x=sentinel3a_time, color='red', linestyle='-.', label='Sentinel-3A/OLCI')
ax.axvline(x=sentinel3b_time, color='green', linestyle='--', label='Sentinel-3B/OLCI')
ax.axvline(x=modis_aqua_time, color='blue', linestyle='-', label='MODIS/Aqua')

box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])  # Shrink width by 20%
plt.legend(title='Depth Category', loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True, shadow=False, fontsize=12, title_fontsize=14)

# Adjust the layout and save
sns.set_context("talk")
fig.autofmt_xdate()
plt.tight_layout(rect=[0, 0.1, 1, 1])
plt.savefig(SAVE_DIR, dpi=500, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.show()