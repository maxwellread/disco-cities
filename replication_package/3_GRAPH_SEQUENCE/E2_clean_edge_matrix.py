import dask.dataframe as dd
import pandas as pd
import os

AUX_LINKS_PATH = r"\data\LINKS\additional_links"
INPATH = r"\data\LINKS\release_links_batches"
OUTPATH = r"\data\LINKS\clean_release_links"


def clean_malformed_rows(df):
    df = df.query('artist_id != "unknown"')
    return df

def clean_writing_credits(df, batch_num):

    writing_patterns = [
        'Written-By',
        'Composed By',
        'Written By',
        'Written-By [Uncredited]',
        'Words By',
        'Music By, Lyrics By',
        'Lyrics By',
        'Songwriter'
    ]
    
    # mask out writing credits
    writing_mask = df['role'].isin(writing_patterns)
    writing_credits_df = df[writing_mask].copy()

    writing_credits_path = os.path.join(AUX_LINKS_PATH, f"writing_credits_{batch_num}.csv")
    
    # safe dask compute
    if hasattr(writing_credits_df, 'compute'):
        writing_credits_df.compute().to_csv(writing_credits_path, index=False)
    else:
        writing_credits_df.to_csv(writing_credits_path, index=False)
    
    # Remove writing credits from base
    cleaned_df = df[~writing_mask].copy()
    
    return cleaned_df

def clean_aux_roles(df):
    aux_roles = ['Lacquer Cut By', 'Remix', 'Compiled By', 'Legal']
    
    # Remove any roles in aux_roles from df
    aux_mask = df['role'].isin(aux_roles)
    
    # Remove translators
    translation_mask = df['role'].str.contains('translat', case=False, na=False)
    
    # Combine masks to remove both aux roles and translation roles
    remove_mask = aux_mask | translation_mask
    
    # Remove rows matching the criteria
    cleaned_df = df[~remove_mask].copy()
    
    return cleaned_df

# Main processing: read in batches 0 to 16 and call each of the functions on them
# Save the result to OUTPATH folder. Do not concatenate the cleaned batches
if __name__ == "__main__":
    # Ensure output directory exists
    os.makedirs(OUTPATH, exist_ok=True)
    os.makedirs(AUX_LINKS_PATH, exist_ok=True)
    
    # Process batches 0 to 16
    for batch_num in range(17):  # 0 to 16 inclusive
        input_file = os.path.join(INPATH, f"master_artist_links_{batch_num}.csv")
        output_file = os.path.join(OUTPATH, f"clean_links_{batch_num}.csv")
        
        print(f"Processing batch {batch_num}...")
        
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"Warning: {input_file} not found, skipping...")
            continue
        
        # Read the batch
        try:
            df = pd.read_csv(input_file)
            print(f"Loaded {len(df)} rows from batch {batch_num}")
            
            # Apply cleaning functions in sequence
            df = clean_malformed_rows(df)
            #print(f"After removing malformed rows: {len(df)} rows")
            
            df = clean_writing_credits(df, batch_num)
            #print(f"After extracting writing credits: {len(df)} rows")
            
            df = clean_aux_roles(df)
            #print(f"After removing aux roles: {len(df)} rows")
            
            # Save cleaned batch
            df.to_csv(output_file, index=False)
            print(f"Saved cleaned batch {batch_num} to {output_file}")
            
        except Exception as e:
            print(f"Error processing batch {batch_num}: {str(e)}")
            continue
    
    print("Processing complete!")
