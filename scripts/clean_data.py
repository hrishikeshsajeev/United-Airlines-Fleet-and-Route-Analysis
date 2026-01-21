"""
Airline Data Cleaning Script

This script processes airline data files (T100 and DB1B) for the 'Airline Project'.
It filters for United Airlines (UA) data, renames columns to a standardized format,
ensures data type safety, and saves the cleaned datasets.

Key Operations:
1.  **T100 Processing**: Filters for 'UA', converts AIRCRAFT_TYPE to string.
2.  **DB1B Processing**: Filters for 'UA', renames columns (ORIGIN, DEST, etc.).
3.  **Automation**: Automatically detects and processes all matching CSV files in the directory.
"""

import pandas as pd
import os
import glob
import sys

# Configuration
BASE_DIR = '/Users/hrishikeshsajeev/Files/Project 1'
T100_FILENAME = 'T_T100D_SEGMENT_US_CARRIER_ONLY-2.csv'
DB1B_PATTERN = 'Origin_and_Destination_Survey_DB1BMarket_2024_*.csv'

# Column Mapping for DB1B
DB1B_RENAME_MAP = {
    'Origin': 'ORIGIN',
    'Dest': 'DEST',
    'MktFare': 'MARKET_FARE',
    'Passengers': 'PAX_WEIGHTING'
}

def clean_t100_data(input_path: str, output_path: str):
    """
    Loads T100 data, filters for United Airlines, and performs type cleaning.
    """
    try:
        print(f"Processing T100 Data: {os.path.basename(input_path)}...")
        df = pd.read_csv(input_path)
        
        # Filter for United Airlines
        df_ua = df[df['UNIQUE_CARRIER'] == 'UA'].copy()
        
        # Ensure AIRCRAFT_TYPE is a clean string
        if 'AIRCRAFT_TYPE' in df_ua.columns:
            df_ua['AIRCRAFT_TYPE'] = df_ua['AIRCRAFT_TYPE'].astype(str).apply(lambda x: x.split('.')[0])
        
        # Save to CSV
        df_ua.to_csv(output_path, index=False)
        print(f"  -> Saved to: {os.path.basename(output_path)}")
        print(f"  -> Rows: {len(df_ua):,}")
        return True
    
    except Exception as e:
        print(f"  [ERROR] Failed to process T100 data: {e}")
        return False

def clean_db1b_data(input_path: str, output_dir: str):
    """
    Loads DB1B data, filters for United Airlines, and renames columns.
    Determines output filename based on quarter in input filename.
    """
    try:
        filename = os.path.basename(input_path)
        print(f"Processing DB1B Data: {filename}...")
        
        df = pd.read_csv(input_path)
        
        # Filter for United Airlines
        # Note: Some DB1B files use 'RPCarrier', checking existence
        if 'RPCarrier' not in df.columns:
             print(f"  [WARNING] 'RPCarrier' column missing in {filename}. Skipping.")
             return False

        df_ua = df[df['RPCarrier'] == 'UA'].copy()
        
        # Rename columns standardizing to T100 format
        df_ua.rename(columns=DB1B_RENAME_MAP, inplace=True)
        
        # Determine output filename (e.g., DB1B_Q1_cleaned.csv)
        # Assumes format: Origin..._2024_X.csv
        parts = filename.replace('.csv', '').split('_')
        suffix = parts[-1]
        
        if suffix.isdigit():
            quarter = suffix
            output_name = f'DB1B_Q{quarter}_cleaned.csv'
        else:
            # Fallback for non-standard names
            output_name = f'DB1B_{suffix}_cleaned.csv'
            
        output_path = os.path.join(output_dir, output_name)
        
        # Save to CSV
        df_ua.to_csv(output_path, index=False)
        print(f"  -> Saved to: {os.path.basename(output_path)}")
        print(f"  -> Rows: {len(df_ua):,}")
        return True

    except Exception as e:
        print(f"  [ERROR] Failed to process {filename}: {e}")
        return False

def main():
    print("="*60)
    print("      AIRLINE PROJECT - DATA CLEANING PIPELINE")
    print("="*60 + "\n")
    
    # 1. Process T100 File
    t100_path = os.path.join(BASE_DIR, T100_FILENAME)
    t100_output = os.path.join(BASE_DIR, 'T100_cleaned.csv')
    
    if os.path.exists(t100_path):
        clean_t100_data(t100_path, t100_output)
    else:
        print(f"[WARNING] T100 file not found at: {t100_path}")
    
    print("-" * 60)
    
    # 2. Process DB1B Files
    search_path = os.path.join(BASE_DIR, DB1B_PATTERN)
    db1b_files = glob.glob(search_path)
    # Filter out any files that might be 'cleaned' versions if pattern overlaps (unlikely with current naming but good practice)
    db1b_raw_files = [f for f in db1b_files if 'cleaned' not in f]
    
    if db1b_raw_files:
        print(f"Found {len(db1b_raw_files)} DB1B raw files. Processing...")
        for file_path in sorted(db1b_raw_files):
            clean_db1b_data(file_path, BASE_DIR)
    else:
        print("[WARNING] No DB1B raw files found.")

    print("\n" + "="*60)
    print("Pipeline Complete.")
    print("="*60)

if __name__ == "__main__":
    main()
