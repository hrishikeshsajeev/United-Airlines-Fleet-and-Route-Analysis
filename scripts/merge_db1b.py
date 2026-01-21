import pandas as pd
import os
import glob

# Configuration
BASE_DIR = '/Users/hrishikeshsajeev/Files/Project 1'
DB1B_PATTERN = 'Origin_and_Destination_Survey_DB1BMarket_2024_*.csv'
OUTPUT_FILE = 'DB1B_Merged.csv'

def process_and_merge():
    print("Starting DB1B Merge Process...")
    
    # Identify files
    search_path = os.path.join(BASE_DIR, DB1B_PATTERN)
    files = sorted(glob.glob(search_path))
    
    # Filter out any cleaned files if they match the pattern (though pattern is specific to raw)
    # The pattern 'Origin_and_Destination_Survey_DB1BMarket_2024_*.csv' matches the raw files.
    # It does NOT match 'DB1B_cleaned.csv' or 'DB1B_Q2_cleaned.csv'.
    
    if not files:
        print("No DB1B files found!")
        return

    print(f"Found {len(files)} files to process.")
    
    data_frames = []
    
    for file_path in files:
        filename = os.path.basename(file_path)
        print(f"\nProcessing: {filename}")
        
        try:
            # 1. Load CSV
            df = pd.read_csv(file_path)
            
            # 2. Standardize Names
            # We need to handle potential variations if RPCarrier is named differently, 
            # though usually it is 'RPCarrier' in DB1B.
            rename_map = {
                'Origin': 'ORIGIN',
                'Dest': 'DEST',
                'MktFare': 'MARKET_FARE',
                'Passengers': 'PAX_WEIGHTING',
                'RPCarrier': 'UNIQUE_CARRIER',
                'UniqueCarrier': 'UNIQUE_CARRIER' # covering bases
            }
            df.rename(columns=rename_map, inplace=True)
            
            # 3. FILTER FIRST: Keep only United Airlines
            if 'UNIQUE_CARRIER' not in df.columns:
                 print(f"Skipping {filename}: 'UNIQUE_CARRIER' column not found (check original column names).")
                 continue
                 
            df_ua = df[df['UNIQUE_CARRIER'] == 'UA'].copy()
            
            # 4. SELECT COLUMNS SECOND
            target_cols = ['ORIGIN', 'DEST', 'MARKET_FARE', 'PAX_WEIGHTING']
            
            # Ensure all columns exist
            missing_cols = [c for c in target_cols if c not in df_ua.columns]
            if missing_cols:
                print(f"Skipping {filename}: Missing columns {missing_cols}")
                continue
                
            df_chunk = df_ua[target_cols].copy()
            
            # Append to list
            data_frames.append(df_chunk)
            print(f"  -> Added {len(df_chunk)} rows.")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # 5. Stack & Save
    if data_frames:
        print("\nConcatenating dataframes...")
        df_final = pd.concat(data_frames, ignore_index=True)
        
        print("\n" + "="*30)
        print("FINAL RESULT")
        print("="*30)
        print(f"Shape: {df_final.shape}")
        print("\nFirst 5 Rows:")
        print(df_final.head())
        
        output_path = os.path.join(BASE_DIR, OUTPUT_FILE)
        df_final.to_csv(output_path, index=False)
        print(f"\nSaved merged file to: {output_path}")
    else:
        print("No data collected to merge.")

if __name__ == "__main__":
    process_and_merge()
