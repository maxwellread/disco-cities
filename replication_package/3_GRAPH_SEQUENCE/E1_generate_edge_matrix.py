# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 16:56:49 2025

EXTRACTS GRAPH INDICENCE MATRIX

@author: maxmo
"""

import xml.etree.ElementTree as ET
import os
import pandas as pd
import time
import gc

file_path = r"\data\discogs_20250201_releases.xml\discogs_20250201_releases.xml"
#OUTFOLDER = r"\data\tests\release_dumps"
OUTFOLDER = r"\data\LINKS\release_links_batches"

#LIMITER = 200000

BATCH_SIZE = 1000000

breaker = 0
recorded_counter = 0
total_counter = 0
batch_counter = 0


# Start iterparse without filtering by tag
context = ET.iterparse(file_path, events=("end",))

# Use a list to accumulate data for faster DataFrame creation
records = []
t0 = time.time()
for event, elem in context:
    if elem.tag == "release":
        release_id = elem.get("id", f"noid_{breaker}")
        for artist in elem.findall('.//extraartists/artist'):
            if artist is not None:
                artist_id = artist.find('id').text if artist.find('id') is not None else "unknown"
                role = artist.find('role').text if artist.find('role') is not None else "unknown"
                records.append((release_id, artist_id, role))
        

        # if breaker > LIMITER: #DEPRECATED - USES LIMITER TO PREVENT TRAWLING ENTIRE DATASET AT ONCE
        #      break
        # breaker += 1
        total_counter += 1
        
        if total_counter % 100000 == 0:
            print("reached " + str(total_counter) + "releases")
        
        #save the dataframe in batches
        if total_counter % BATCH_SIZE == 0:
            edges_frame = pd.DataFrame(records, columns=["release_id", "artist_id", "role"])
            edges_frame = edges_frame.drop_duplicates(ignore_index=True)
            output_path = os.path.join(OUTFOLDER, f"master_artist_links_{batch_counter}.csv")
            edges_frame.to_csv(output_path, index=False)
            print(f"Data saved to {output_path}")
            batch_counter += 1
            
            del edges_frame
            del records
            gc.collect()
            records = []
        

        
        # Clear element to free memory
        elem.clear()


t2 = time.time()

print("total time: " + str(t2 - t0))


