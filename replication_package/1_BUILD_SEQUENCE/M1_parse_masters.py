# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 20:52:18 2025

WHAT TO SNAG:
    - 

@author: maxmo
"""

import os
import pandas as pd
import xml.etree.ElementTree as ET

LIMIT_OUTPUT = False  # Set to True to limit output for testing
LIMITER = 2000
breaker = 0
recorded_counter = 0
total_counter = 0

INPATH = r"\data\discogs_20250401_masters.xml"
OUTFOLDER = r"\data"


context = ET.iterparse(INPATH, events=("end",))

outframe = pd.DataFrame()

records = []

for event, elem in context:
    if elem.tag == "master":
        master_id = elem.get("id", f"noid_{breaker}")
        output_path = os.path.join(OUTFOLDER, f"{master_id}.xml")
        
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
        else:
            genre_list = []
            
        styles = elem.find("styles")
        if styles is not None:
            style_list = [style.text for style in styles.findall("style")]
        else:
            style_list = []
            
        artist_ids = [artist_id.text for artist_id in elem.findall(".//artist/id") if artist_id is not None]
        
        # Extract year and title
        year = elem.find("year").text if elem.find("year") is not None else None
        title = elem.find("title").text if elem.find("title") is not None else None

        records.append([master_id, artist_ids, genre_list, style_list, data_quality, year, title])
        
        
        # with open(output_path, "wb") as f:
        #            f.write(ET.tostring(elem, encoding="utf-8"))
        if LIMIT_OUTPUT:
            if breaker > LIMITER:
                break
            breaker += 1
            total_counter += 1
        
masters_frame = pd.DataFrame(records, columns=["master_id", "artist_ids", "genres", "styles", "data_quality", "year", "title"])

output_path = os.path.join(OUTFOLDER, "masters_v2.csv")
masters_frame.to_csv(output_path, index=False)
print(f"Data saved to {output_path}")