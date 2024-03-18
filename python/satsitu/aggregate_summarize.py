import pandas as pd
import os

def load_and_rename(sensor_name, data_dir):
    # Update the path for reading the CSV file using the provided data directory
    df = pd.read_csv(os.path.join(data_dir, f'{sensor_name}_l2.csv'))
    
    # Rename columns to include the sensor name
    df.rename(columns={
        'insitu_chl_1x1': f'{sensor_name}_insitu_chl_1x1',
        'insitu_chl_2x2': f'{sensor_name}_insitu_chl_2x2',
        'insitu_chl_3x3': f'{sensor_name}_insitu_chl_3x3'
    }, inplace=True)
    return df

def main():
    # Assume the script is running from its current directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Calculate the relative path to the data directory from the script's location
    # This step navigates up to the Thesis directory, then down to the data directory
    data_dir = os.path.abspath(os.path.join(script_dir, '../../../data/satsitu/aggregated_data'))
    
    # Define sensor names
    sensors = ['hawkeye', 'modisa', 's3a', 's3b', 'oli8']

    # Load and rename columns for each sensor, passing the calculated data directory as an argument
    dfs = [load_and_rename(sensor, data_dir) for sensor in sensors]

    # Concatenate all DataFrames column-wise
    master_df = pd.concat(dfs, axis=1)

    # Define the path where the output CSV file should be saved
    master_csv_path = os.path.join(data_dir, 'master_dataset_l2.csv')
    
    # Save the concatenated DataFrame to the master CSV file
    master_df.to_csv(master_csv_path, index=False)
    
    print(f'Master dataset saved to {master_csv_path}')

if __name__ == '__main__':
    main()
