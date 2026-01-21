import pandas as pd
import os

# Define file paths
base_dir = '/Users/hrishikeshsajeev/Files/Project 1'
t100_file = os.path.join(base_dir, 'T_T100D_SEGMENT_US_CARRIER_ONLY-2.csv')
db1b_file = os.path.join(base_dir, 'Origin_and_Destination_Survey_DB1BMarket_2024_1.csv')

print(f"Loading files from {base_dir}...\n")

try:
    # Load T100
    print(f"Loading T100 data from: {os.path.basename(t100_file)}")
    df_t100 = pd.read_csv(t100_file)
    print("T100 Columns:")
    print(df_t100.columns.tolist())
    print("\nT100 Head:")
    print(df_t100.head())
    print("\n" + "="*50 + "\n")

    # Load DB1B
    print(f"Loading DB1B data from: {os.path.basename(db1b_file)}")
    df_db1b = pd.read_csv(db1b_file)
    print("DB1B Columns:")
    print(df_db1b.columns.tolist())
    print("\nDB1B Head:")
    print(df_db1b.head())

except Exception as e:
    print(f"An error occurred: {e}")
