# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 21:02:20 2025

@author: maxmo
"""

import xml.etree.ElementTree as ET
import os
import pandas as pd

file_path = r"\data\discogs_20250201_releases.xml\discogs_20250201_releases.xml"
#OUTFOLDER = r"\data\tests\release_dumps"
OUTFOLDER = r"\data"

USE_LIMITER = False
LIMITER = 1000

breaker = 0
recorded_counter = 0
total_counter = 0

# List of specific release IDs to match (without the leading 'r')
specific_release_ids = ["663096", "421057", "2326125", "1299029", "6711419", "20067715", "17991358"]

# Define the output folder for specific releases
specific_releases_folder = r"\data\tests\specific_releases_tests"
os.makedirs(specific_releases_folder, exist_ok=True)  # Create the folder if it doesn't exist

# Start iterparse without filtering by tag
context = ET.iterparse(file_path, events=("end",))

# Use a list to accumulate data for faster DataFrame creation
records = []

for event, elem in context:
    if elem.tag == "release":
        release_id = elem.get("id", f"noid_{breaker}")
        
        # Check if the release_id matches one of the specific IDs
        if release_id in specific_release_ids:
            # Save the entire XML of the release to the specific folder
            output_file = os.path.join(specific_releases_folder, f"release_{release_id}.xml")
            with open(output_file, "wb") as file:
                file.write(ET.tostring(elem, encoding="utf-8"))
            print(f"Saved specific release XML to {output_file}")

        master_id = elem.find("master_id").text if elem.find("master_id") is not None else f"master_noid_{breaker}"
        #notes = elem.find("notes").text if elem.find("notes") is not None else ""
        
        data_quality_marker = elem.find("data_quality").text
        data_quality = -1
        if data_quality_marker == "Correct":
            data_quality = 1
        elif data_quality_marker == "Complete and Correct":
            data_quality = 2
        elif data_quality_marker == "Needs Vote":
            data_quality = 0
            
        genres = elem.find("genres")
        if genres is not None:
            genre_list = [genre.text for genre in genres.findall("genre")]
            genre = ", ".join(genre_list)
        else:
            genre = "no_genre"
        
        companies = elem.find("companies")
        recorded_at_ids = []  # Initialize a list to store multiple IDs
        if companies is not None:
            for company in companies.findall("company"):
                entity_type_name = company.find("entity_type_name")
                if entity_type_name is not None and entity_type_name.text == "Recorded At":
                    company_id = company.find("id")
                    if company_id is not None:
                        recorded_at_ids.append(company_id.text)  # Append each ID to the list
                        print(f"Recorded At Company ID: {company_id.text}")
                        recorded_counter += 1

        # Join all recorded_at IDs into a single string
        recorded_at_string = ", ".join(recorded_at_ids)

        # Append data to the list
        records.append([release_id, master_id, recorded_at_string, data_quality])
        
        if USE_LIMITER:
            if breaker > LIMITER:
                break
            breaker += 1
            total_counter += 1
        
        # Clear element to free memory
        elem.clear()

# Convert list to DataFrame after processing
outframe = pd.DataFrame(records, columns=["release_id", "master_id", "recorded_at", "data_quality"])

# Save DataFrame to a file once at the end
output_path = os.path.join(OUTFOLDER, "releases_v2.csv")
outframe.to_csv(output_path, index=False)
print(f"Data saved to {output_path}")