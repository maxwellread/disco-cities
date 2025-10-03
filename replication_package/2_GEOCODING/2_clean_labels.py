# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 17:54:57 2025

CLEANS LABELS THAT MATCH FROM THE 'RECORDED_AT' TAG IN THE RELEASE DATA

@author: maxmo
"""

import pandas as pd
import re
import os

RELEASES_PATH = r""
INPATH = r"\data\release_contacts_v1.csv"
OUTPATH = r"\data\L2_clean_labels.csv"

EMAIL_REGEX = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
TELEPHONE_REGEX = r"(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
UK_POSTCODE_REGEX = r"[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}"

WORDSET = ['tel', 'fax', 'phone', 'email', 'recordings', 'telephone']
TAGSET = ['current', 'obsolete']

full_df = pd.read_csv(INPATH)
#full_df = full_df.sample(10000)
full_df = full_df[full_df['Contact Info'].notna()]
full_df = full_df[['Contact Info', 'ID', 'Name', 'profile']]
full_df = full_df.rename(columns={'ID': 'recorded_id'})
full_df = full_df.drop_duplicates()
df = full_df #.sample(1000)

# Track initial unique recorded_id count
initial_unique_recorded_id = df['recorded_id'].nunique()
print(f"Initial unique recorded_id count: {initial_unique_recorded_id}")

df['text_block'] = df['Contact Info'].str.split(r'(?:\r?\n){2,}')
df = df.explode('text_block').reset_index(drop=True)

# Track after exploding text blocks
after_explode_unique_recorded_id = df['recorded_id'].nunique()
print(f"After exploding text blocks: {after_explode_unique_recorded_id}")

df['text_block'] = df['text_block'].apply(
    lambda tb: '\n'.join([line for line in tb.splitlines() if not re.search(EMAIL_REGEX, line, flags=re.IGNORECASE)])
)
df['text_block'] = df['text_block'].apply(
    lambda tb: '\n'.join([line for line in tb.splitlines() if not re.search(TELEPHONE_REGEX, line, flags=re.IGNORECASE)])
)

for word in WORDSET:
    df['text_block'] = df['text_block'].apply(
        lambda tb: '\n'.join([line for line in tb.splitlines() if not re.search(fr"\b{word}\b", line, flags=re.IGNORECASE)])
    )


for tag in TAGSET:
    df[tag] = df['text_block'].str.contains(fr"\b{tag}\b", na=False, case=False).astype(int)
    df['text_block'] = df['text_block'].str.replace(fr"\b{tag}\b", '', case=False, regex=True)

# 1. Remove studio name, "inc.", studio name without spaces, and "(n)" disambiguators (row-wise)
def clean_name_from_textblock(row):
    tb = row['text_block']
    name = row['Name']
    if pd.isna(name):
        return tb
    # Remove studio name (case-insensitive, word boundaries)
    name_pattern = re.escape(name)
    tb = re.sub(fr"\b{name_pattern}\b", '', tb, flags=re.IGNORECASE)
    # Remove studio name without spaces
    name_nospace = name.replace(' ', '')
    if name_nospace:
        name_nospace_pattern = re.escape(name_nospace)
        tb = re.sub(fr"\b{name_nospace_pattern}\b", '', tb, flags=re.IGNORECASE)
    # Remove "inc." (case-insensitive, word boundaries)
    tb = re.sub(r"\binc\.\b", '', tb, flags=re.IGNORECASE)
    # Remove "(n)" type disambiguators (where n is an int)
    tb = re.sub(r"\(\d+\)", '', tb)
    return tb

df['text_block'] = df.apply(clean_name_from_textblock, axis=1)

# Track after name cleaning
after_name_clean_unique_recorded_id = df['recorded_id'].nunique()
print(f"After name cleaning: {after_name_clean_unique_recorded_id}")

# 3. Remove any line within the text block that starts and ends with brackets or parentheses
def remove_bracketed_lines(tb):
    return '\n'.join([
        line for line in tb.splitlines()
        if not re.match(r'^\s*[\[\(].*[\]\)]\s*$', line.strip())
    ])
df['text_block'] = df['text_block'].apply(remove_bracketed_lines)

# Track after removing bracketed lines
after_bracket_clean_unique_recorded_id = df['recorded_id'].nunique()
print(f"After removing bracketed lines: {after_bracket_clean_unique_recorded_id}")

# 5. Remove line within the text block if the line only says "Address" (case-insensitive, after stripping non-alphanumerics)
def remove_address_lines(tb):
    lines = []
    for line in tb.splitlines():
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', line).lower()
        if cleaned != 'address':
            lines.append(line)
    return '\n'.join(lines)
df['text_block'] = df['text_block'].apply(remove_address_lines)

# Track after removing address lines
after_address_clean_unique_recorded_id = df['recorded_id'].nunique()
print(f"After removing address lines: {after_address_clean_unique_recorded_id}")

# Remove lines within each text block that contain only non-alphanumeric characters
df['text_block'] = df['text_block'].apply(
    lambda tb: '\n'.join([line for line in tb.splitlines() if re.search(r'[a-zA-Z0-9]', line)])
)

# Track after removing non-alphanumeric lines
after_nonalpha_clean_unique_recorded_id = df['recorded_id'].nunique()
print(f"After removing non-alphanumeric lines: {after_nonalpha_clean_unique_recorded_id}")

# Store row count before dropping non-alphabet text blocks
rows_before_alphabet_filter = len(df)

# ✅ TODO - DROP IF TEXT BLOCK CONTAINS ONLY NON-ALPHABET CHARACTERS
df = df[df['text_block'].str.contains(r'[a-zA-Z]', na=False)]

# Calculate and print percentage of rows dropped
rows_after_alphabet_filter = len(df)
rows_dropped = rows_before_alphabet_filter - rows_after_alphabet_filter
percentage_dropped = (rows_dropped / rows_before_alphabet_filter) * 100
print(f"Rows dropped after alphabet filter: {rows_dropped} ({percentage_dropped:.2f}%)")

# Track after dropping non-alphabet text blocks
final_unique_recorded_id = df['recorded_id'].nunique()
print(f"After dropping non-alphabet text blocks: {final_unique_recorded_id}")

# ✅ TODO - CREATE A VARIABLE 'YEAR' FOR A VALID YEAR - MATCH FOUR NUMBERS BETWEEN 1900 AND 2025
df['YEAR'] = df['text_block'].str.extract(r'\b(19[0-9]{2}|20[0-2][0-9]|2025)\b', expand=False)
#TODO - edit above block to capture start and end years

# ✅ TODO - REMOVE ANY WEIRD "[\b]" type entries
df['text_block'] = df['text_block'].str.replace(r'\[\\b\]', '', regex=True)

# ✅ TODO - drop "located in"
df['text_block'] = df['text_block'].str.replace(r'\blocated in\b', '', case=False, regex=True)

print("saving")
print(len(df.index))
print(f"Attempting to save to: {OUTPATH}")
print(f"Directory exists: {os.path.exists(os.path.dirname(OUTPATH))}")
df.to_csv(OUTPATH, index=False)
print(f"File exists after save: {os.path.exists(OUTPATH)}")
if os.path.exists(OUTPATH):
    print(f"File size: {os.path.getsize(OUTPATH)} bytes")
