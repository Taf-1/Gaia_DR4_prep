import pandas as pd
import glob as g 
from pathlib import Path
import os

if __name__ == "__main__":
    # Define the path to the directory containing the CSV files
    csv_directory = Path(__file__).resolve().parent.parent / 'src/data'

    # Use glob to find all parquet files in the directory
    parquet_files = g.glob(str(csv_directory / '*.parquet'))

    # Initialize an empty dict to hold the DataFrames
    dataframes = {}

    # Loop through the lst of parquet files and read each one into a DataFrame
    for parquet_file in parquet_files:
        df = pd.read_parquet(parquet_file)
        # Store the DataFrame in the dict with the filename (without extension) as the key
        filename = os.path.basename(parquet_file).replace('.parquet', '')
        dataframes[filename] = df

    # Examine the schema and contents of each DataFrame
    for i, df in enumerate(dataframes):
        print(f"DataFrame {i}: {df}")
        print(dataframes[df].info())
        print(dataframes[df].head())

    # Check if there are overlapping source_ids between the two DataFrames
    if 'gaia_photometry_sources' in dataframes and 'gaia_eb_sources' in dataframes:
        df1 = dataframes['gaia_photometry_sources']
        df2 = dataframes['gaia_eb_sources']

        overlapping_source_ids = set(df1['source_id']).intersection(set(df2['source_id']))
        print(f"Number of overlapping source_ids: {len(overlapping_source_ids)}")
        print(f"Overlapping source_ids: {overlapping_source_ids}")
    else:
        print("One or both DataFrames are missing.")

