# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 17:04:57 2025

@author: maxmo
"""

import xml.etree.ElementTree as ET
import pandas as pd
import random

OUTPATH = r"\data\L1_LABELS.csv"

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    data = []  # List to store extracted data

    # --- Sample and save 100 random labels as XML ---
    labels = root.findall("label")
    sample_labels = random.sample(labels, min(100, len(labels)))
    for i, label in enumerate(sample_labels):
        sample_tree = ET.ElementTree(label)
        outpath = rf"\data\tests\labels_dumps\label_sample_{i+1}.xml"
        sample_tree.write(outpath, encoding="utf-8", xml_declaration=True)

    # Loop through all <label> elements
    for label in labels:
        name = label.find("name").text if label.find("name") is not None else ""
        if "Not On Label" in name:
            continue

        print(name) 
        label_id = label.find("id").text if label.find("id") is not None else ""
        contact_info = label.find("contactinfo").text if label.find("contactinfo") is not None else ""

        # Normalize contact info
        contact_info = contact_info.replace("&#13;", "\n").strip()

        # Get data_quality and profile
        data_quality_marker = label.find("data_quality").text if label.find("data_quality") is not None else None
        data_quality = -1
        if data_quality_marker == "Correct":
            data_quality = 1
        elif data_quality_marker == "Complete and Correct":
            data_quality = 2
        elif data_quality_marker == "Needs Vote":
            data_quality = 0

        profile = label.find("profile").text if label.find("profile") is not None else ""

        # Extract sublabel IDs
        sublabels = label.find("sublabels")
        sublabel_ids = []
        if sublabels is not None:
            sublabel_ids = [sublabel.get("id") for sublabel in sublabels.findall("label") if sublabel.get("id")]
        
        data.append([label_id, name, contact_info, ",".join(sublabel_ids), data_quality, profile])  # Append to list

    # Create a DataFrame
    df = pd.DataFrame(data, columns=["ID", "Name", "Contact Info", "Sublabel IDs", "label_data_quality", "profile"])
    
    return df

# Example usage
file_path = r"\data\discogs_20250201_labels.xml"
df = parse_xml(file_path)
#df = df[df["Contact Info"].str.strip() != ""]
df.to_csv(OUTPATH)

#df = parse_xml(file_path)
#print(df)
