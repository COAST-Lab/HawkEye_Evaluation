import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Constants and configurations
DATA_DIR = '/Users/macbook/HawkEye_Evaluation/data/acrobat/050523/transects'
SAVE_DIR = '/Users/macbook/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects'

QC_PARAMS = {
    'time_increment': pd.Timedelta(minutes=15),
    'turbidity_min': 0,
    'turbidity_max': 10,
    'turbidity_spike_threshold': 5
}

# Create SAVE_DIR if it does not exist
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Function to reverse rows of DataFrame
def reverse_dataframe_rows(df):
    return df.iloc[::-1].reset_index(drop=True)

# Function for QC tests with reporting for each transect
def perform_qc_tests(df, qc_params):
    # QC report setup
    qc_report = {
        'timing_gap_flags': 0,
        'range_flags': 0,
        'spike_flags': 0,
        'total_points_removed': 0
    }

    # QC tests
    df['timestamp'] = pd.to_datetime(df['time'], unit='s')
    timing_gap_flags = (df['timestamp'].diff().abs() > qc_params['time_increment']) | df['timestamp'].isnull()
    range_flags = (df['turbidity'] < qc_params['turbidity_min']) | (df['turbidity'] > qc_params['turbidity_max'])
    spike_flags = df['turbidity'].diff().abs() > qc_params['turbidity_spike_threshold']

    # Flagging and replacing turbidity values
    flagged = timing_gap_flags | range_flags | spike_flags
    df.loc[flagged, 'turbidity'] = pd.NA

    # Update report
    qc_report['timing_gap_flags'] += timing_gap_flags.sum()
    qc_report['range_flags'] += range_flags.sum()
    qc_report['spike_flags'] += spike_flags.sum()
    qc_report['total_points_removed'] += flagged.sum()

    return df, qc_report

# Function to process a single file
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
        print(f"Error processing file {file}: {e}")
        return None, {}, None
    
# Check if the data directory exists
if not os.path.exists(DATA_DIR):
    print(f"Data directory '{DATA_DIR}' does not exist.")
else:
    combined_data = pd.DataFrame()
    qc_reports = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_file, file): file for file in os.listdir(DATA_DIR) if file.endswith('.xlsx')}
        for future in tqdm(futures):
            result, qc_report, transect_id = future.result()
            qc_reports[transect_id] = qc_report
            if result is not None:
                combined_data = pd.concat([combined_data, result], ignore_index=True)

    # Split the cleaned (and reversed if even) data into separate files based on transect ID
    for transect_id, data in tqdm(combined_data.groupby('transect_id')):
        output_file_path = os.path.join(SAVE_DIR, f'transect_{transect_id}.xlsx')
        data.to_excel(output_file_path, index=False)
        print(f'Processed DataFrame for Transect {transect_id} saved to {output_file_path}')

# Print QC reports for each transect
print("\nQC Test Reports for Each Transect:")
for transect_id, report in qc_reports.items():
    print(f"\nTransect ID: {transect_id}")
    for test, count in report.items():
        print(f"{test}: {count}")