# -*- coding: utf-8 -*-
"""
Created on Thu Apr  3 17:59:12 2025

FILTERS THE LIST OF LABELS TO THOSE MATCHING LISTED RECORDING STUDIOS IN THE RELEASE DATA

@author: maxmo
"""

import pandas as pd
import os


contacts_path = r"\data\L1_LABELS.csv"
releases_path = r"\data\LINKS\recorded_master_links_v1.csv"
outpath = r"\data\release_contacts_v1.csv"


contacts = pd.read_csv(contacts_path)
releases = pd.read_csv(releases_path)

print(releases.columns)
print(contacts.columns)

releases_sample = releases.sample(1000)
contacts_sample = contacts.sample(1000)

df = pd.merge(releases, contacts, left_on='recorded_at', right_on='ID', how='left')
print(f"Total releases: {len(releases)}")
print(f"Releases with valid recorded_at ID: {df['ID'].notna().sum()}")

valid_contact_percentage = df['Contact Info'].notna().mean() * 100
print(f"Percentage of release_ids with valid contact info: {valid_contact_percentage:.2f}%")

data_quality_with_contact = df[df['Contact Info'].notna()]['data_quality'].gt(0).mean() * 100
data_quality_without_contact = df[df['Contact Info'].isna()]['data_quality'].gt(0).mean() * 100
print(f"Percentage of data_quality > 0 with valid contact info: {data_quality_with_contact:.2f}%")
print(f"Percentage of data_quality > 0 without valid contact info: {data_quality_without_contact:.2f}%")

valid_contacts_df = df[(df['Contact Info'].notna()) | (df['profile'].notna())]

valid_master_id_percentage = df[df['master_id'].notna() & df['Contact Info'].notna()]['master_id'].nunique() / df['master_id'].nunique() * 100
print(f"Percentage of unique master_ids with valid contact info: {valid_master_id_percentage:.2f}%")

valid_contacts_df.to_csv(outpath, index=False)

