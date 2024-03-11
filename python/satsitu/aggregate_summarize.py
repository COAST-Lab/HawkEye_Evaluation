import pandas as pd

def load_and_rename(sensor_name):
    # Define the path to the directory where the data files are located
    data_dir = "/Users/mitchtork/HawkEye_Evaluation/data/satsitu/aggregated_data"
    
    # Update the path for reading the CSV file
    df = pd.read_csv(f'{data_dir}/{sensor_name}.csv')
    
    # Rename columns
    df.rename(columns={
        'insitu_chl_1x1': f'{sensor_name}_insitu_chl_1x1',
        'insitu_chl_2x2': f'{sensor_name}_insitu_chl_2x2',
        'insitu_chl_3x3': f'{sensor_name}_insitu_chl_3x3'
    }, inplace=True)
    return df

def main():
    # Define sensor names
    sensors = ['hawkeye', 'modisa', 's3a', 's3b', 'oli8']

    # Load and rename columns for each sensor
    dfs = [load_and_rename(sensor) for sensor in sensors]

    # Concatenate all DataFrames column-wise
    master_df = pd.concat(dfs, axis=1)

    # Define the path where the output CSV file should be saved
    output_dir = "/Users/mitchtork/HawkEye_Evaluation/data/satsitu/aggregated_data"
    master_csv_path = f'{output_dir}/master_dataset.csv'
    
    # Save the concatenated DataFrame to the master CSV file
    master_df.to_csv(master_csv_path, index=False)
    
    print(f'Master dataset saved to {master_csv_path}')

if __name__ == '__main__':
    main()
