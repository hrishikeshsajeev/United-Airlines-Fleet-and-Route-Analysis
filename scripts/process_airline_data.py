import pandas as pd
import os

# Set the path to my files
# Make sure to change this if your files are somewhere else
base_path = '/Users/hrishikeshsajeev/Files/Project 1'

print("Starting the T100 data cleaning...")

# 1. READ THE T100 FILE
t100_file = base_path + '/T_T100D_SEGMENT_US_CARRIER_ONLY-2.csv'
df_t100 = pd.read_csv(t100_file)

# Filter for United Airlines
# UNIQUE_CARRIER is the column name for the airline code
df_t100 = df_t100[df_t100['UNIQUE_CARRIER'] == 'UA']

# Fix the aircraft type column
# Convert it to string so it doesn't look like a number
df_t100['AIRCRAFT_TYPE'] = df_t100['AIRCRAFT_TYPE'].astype(str)

# Save the cleaned file
df_t100.to_csv(base_path + '/T100_cleaned.csv', index=False)
print("Done with T100!")


# %%
# Now we do the DB1B files
print("Starting DB1B merging...")

all_data = []

# Loop through the 4 quarters 
# The files are named with _1, _2, _3, _4 at the end
for i in range(1, 5):
    filename = 'Origin_and_Destination_Survey_DB1BMarket_2024_' + str(i) + '.csv'
    full_path = base_path + '/' + filename
    
    print("Reading file:", filename)
    df = pd.read_csv(full_path)
    
    # Rename the columns to look nice
    # Using a dictionary to map old names to new names
    df = df.rename(columns={
        'Origin': 'ORIGIN',
        'Dest': 'DEST',
        'MktFare': 'MARKET_FARE',
        'Passengers': 'PAX_WEIGHTING',
        'RPCarrier': 'UNIQUE_CARRIER'
    })
    
    # Filter for United Airlines again
    df = df[df['UNIQUE_CARRIER'] == 'UA']
    
    # Keep only the columns we need
    df = df[['ORIGIN', 'DEST', 'MARKET_FARE', 'PAX_WEIGHTING']]
    
    # Add this quarter's data to our list
    all_data.append(df)

# Put it all together into one big dataframe
final_df = pd.concat(all_data)

# Save the final merged file
print("Saving the final file...")
final_df.to_csv(base_path + '/DB1B_Merged.csv', index=False)

print("Finished!")
print("Total rows:", len(final_df))
