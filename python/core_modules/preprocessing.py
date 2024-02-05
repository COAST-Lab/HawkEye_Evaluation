import os
import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import time

BASE_DIR = '/Users/mitchtork/HawkEye_Eval/'
DATA_DIR = os.path.join(BASE_DIR, 'data/acrobat/050523/transects')
SAVE_DIR = os.path.join(BASE_DIR, 'data/acrobat/050523/transects/processed_transects')
QC_REPORT_DIR = os.path.join(BASE_DIR, 'data/acrobat/050523/transects/processed_transects/QC_reports')
QC_REPORT = os.path.join(QC_REPORT_DIR, 'QC_report.txt')
OUTPUT_DATASET_FILE = os.path.join(SAVE_DIR, 'processed_dataset.xlsx')

QC_PARAMS = {
    'time_increment': pd.Timedelta(minutes=15),
    'temp_min': 19.5, 'temp_max': 20.5, 'temp_spike_threshold': 0.5,
    'conductivity_min': 4.40, 'conductivity_max': 4.82, 'conductivity_spike_threshold': 0.2,
    'density_min': 1022, 'density_max': 1025, 'density_spike_threshold': 1,
    'salinity_min': 34.9, 'salinity_max': 35.05, 'salinity_spike_threshold': 0.07,
    'turbidity_min': 0.00, 'turbidity_max': 11, 'turbidity_spike_threshold': 5,
    'chlor_a_min': 0.00, 'chlor_a_max': 2.20, 'chlor_a_spike_threshold': 1,
    'ox_sat_min': 7.36, 'ox_sat_max': 7.54, 'ox_sat_spike_threshold': 0.1
    # Adjust the min, max, and spike threshold values as needed
}

# Create directories if they do not exist
for directory in [SAVE_DIR, QC_REPORT_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to reverse rows of DataFrame
def reverse_dataframe_rows(df):
    return df.iloc[::-1].reset_index(drop=True)

def perform_qc_tests(df, qc_params):
    qc_report = {'timing_gap_flags': 0, 'total_points_removed': 0}
    flagged = pd.Series([False] * len(df))

    # Time QC
    df['timestamp'] = pd.to_datetime(df['time'], unit='s')
    timing_gap_flags = (df['timestamp'].diff().abs() > qc_params['time_increment']) | df['timestamp'].isnull()
    flagged |= timing_gap_flags

    # Function to handle QC for a specific data type
    def qc_for_data_type(column, min_val, max_val, spike_threshold):
        if column not in df.columns:
            return pd.Series([False] * len(df))  # Column not present

        range_flags = (df[column] < min_val) | (df[column] > max_val)
        spike_flags = df[column].diff().abs() > spike_threshold
        df.loc[range_flags | spike_flags, column] = pd.NA
        qc_report[f'{column}_range_flags'] = range_flags.sum()
        qc_report[f'{column}_spike_flags'] = spike_flags.sum()
        return range_flags | spike_flags

    # Apply QC for each data type
    for data_type in ['temp', 'conductivity', 'density', 'salinity', 'turbidity', 'chlor_a', 'ox_sat']:
        flagged |= qc_for_data_type(data_type, qc_params[f'{data_type}_min'], qc_params[f'{data_type}_max'], qc_params[f'{data_type}_spike_threshold'])

    # Update report
    qc_report['timing_gap_flags'] = timing_gap_flags.sum()
    qc_report['total_points_removed'] = flagged.sum()

    return df, qc_report

def process_file(file):
    try:
        file_path = os.path.join(DATA_DIR, file)
        df = pd.read_excel(file_path, engine='openpyxl')
        cleaned_df, qc_report = perform_qc_tests(df, QC_PARAMS)

        # Extract transect ID from filename and reverse if odd
        transect_id_str = file.split('.')[0].replace('transect', '')  # Remove 'transect' from the filename
        transect_id = int(transect_id_str)  # Convert to integer
        if transect_id % 2 != 0:  # Check if the transect ID is odd
            cleaned_df = reverse_dataframe_rows(cleaned_df)

        return cleaned_df, qc_report, transect_id
    except Exception as e:
        logging.error(f"Error processing file {file}: {e}")
        print(f"Error processing file {file}: {e}")
        return None, {}, None

# Check if the data directory exists
if not os.path.exists(DATA_DIR):
    print(f"Data directory '{DATA_DIR}' does not exist.")
else:
    combined_data = pd.DataFrame()
    qc_reports = {}

    # Filter out temporary and irrelevant files
    valid_files = [file for file in os.listdir(DATA_DIR) if file.endswith('.xlsx') and not file.startswith('~$')]

    # Sort files by transect ID if necessary
    sorted_files = sorted(valid_files, key=lambda x: int(x.replace('transect', '').split('.')[0]))

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_file, file): file for file in sorted_files}
        for future in tqdm(futures):
            result, qc_report, transect_id = future.result()
            qc_reports[transect_id] = qc_report
            if result is not None:
                combined_data = pd.concat([combined_data, result], ignore_index=True)

    # Save the entire processed dataset to an Excel file
    combined_data.to_excel(OUTPUT_DATASET_FILE, index=False)
    print(f'Entire processed dataset saved to {OUTPUT_DATASET_FILE}')
    
    # Split the cleaned (and reversed if even) data into separate files based on transect ID
    for transect_id, data in tqdm(combined_data.groupby('transect_id')):
        output_file_path = os.path.join(SAVE_DIR, f'transect_{transect_id}.xlsx')
        data.to_excel(output_file_path, index=False)
        print(f'Processed DataFrame for Transect {transect_id} saved to {output_file_path}')

    # Save QC reports to a file
    try:
        with open(QC_REPORT, 'w') as report_file:
            for transect_id, report in qc_reports.items():
                report_file.write(f"\nTransect ID: {transect_id}\n")
                for test, count in report.items():
                    report_file.write(f"{test}: {count}\n")
    except IsADirectoryError:
        print(f"Error: {QC_REPORT} is a directory, not a file.")

# Print QC reports for each transect
print("\nQC Test Reports for Each Transect:")
for transect_id, report in qc_reports.items():
    print(f"\nTransect ID: {transect_id}")
    for test, count in report.items():
        print(f"{test}: {count}")