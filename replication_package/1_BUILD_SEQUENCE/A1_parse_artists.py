# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 20:31:35 2025

@author: maxmo
"""

import xml.etree.ElementTree as ET
import os
import pandas as pd

INPATH = r"\data\discogs_20250401_artists.xml"
#OUTFOLDER = r"\data\tests\release_dumps"
TEST_OUTFOLDER = r"\data\tests\artist_dumps"
OUTFOLDER= r"\data"

LIMITER = 100

breaker = 0
recorded_counter = 0
total_counter = 0

# Start iterparse without filtering by tag
context = ET.iterparse(INPATH, events=("end",))

# Use a list to accumulate data for faster DataFrame creation
records = []

for event, elem in context:
    if elem.tag == "artist":
        artist_id = elem.find("id").text if elem.find("id") is not None else f"noid_{breaker}"
        name = elem.find("name").text if elem.find("name") is not None else f"unnamed_{breaker}"
        output_path = os.path.join(TEST_OUTFOLDER, f"{name}.xml")
        
        data_quality_marker = elem.find("data_quality").text
        data_quality = -1
        if data_quality_marker == "Correct":
            data_quality = 1
        elif data_quality_marker == "Complete and Correct":
            data_quality = 2
        elif data_quality_marker == "Needs Vote":
            data_quality = 0
            
        member_ids = [member.get('id') for member in elem.findall('.//members/name')]
                     
        # with open(output_path, "wb") as f:
        #    f.write(ET.tostring(elem, encoding="utf-8"))
        
        records.append([artist_id, member_ids, name, data_quality])
        
        # if breaker > LIMITER:
        #     break
        breaker += 1
        total_counter += 1
        
        # Clear element to free memory
        elem.clear()

# Convert list to DataFrame after processing
artist_frame = pd.DataFrame(records, columns=["artist_id", "member_ids", "name", "data_quality"])
output_path = os.path.join(OUTFOLDER, "artists_v1.csv")
artist_frame.to_csv(output_path, index=False)
print(f"Data saved to {output_path}")