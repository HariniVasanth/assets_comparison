import logging
import os
import sys
import time
import csv

import pandas as pd

import requests

import planon

# =============================================================
# LOGGING
# =============================================================

log_level = "INFO"
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logging.basicConfig(stream=sys.stdout, level=log_level, format=log_format)
# logging.basicConfig(filename='logging.log', level = log_level, format = log_format)

# Set the log to use GMT time zone
logging.Formatter.converter = time.gmtime

# Add milliseconds
logging.Formatter.default_msec_format = "%s.%03d"

log = logging.getLogger(__name__)

# =======================
# PLANON
# =======================

planon.PlanonResource.set_site(site=os.environ["PLANON_API_URL"])
planon.PlanonResource.set_header(jwt=os.environ["PLANON_API_KEY"])

# planon_asset_classifications = {asset_classification.Syscode: asset_classification for asset_classification in planon.AssetClassification.find()}
# planon_item_groups = {item_group.Syscode: item_group for item_group in planon.ItemGroup.find()}
# planon_properties = {property.Syscode: property for property in planon.Property.find()}
# planon_spaces = {space.Syscode: space for space in planon.Space.find()}


# =======================
# MAIN
# Assign/Read name column csv file
# Parse the last 7 characters from each asset's name
# Create a new column with the parsed names
# =======================

# Assign/Read name column csv file
csv_file_path = "input/input_assets.csv"
data = pd.read_csv(csv_file_path)

# Parse and extract columns
names_column = data['Name']
parsed_names = [name[-7:] for name in names_column]
data['ParsedName']=parsed_names
ip_address_column = data['Address'].str.split('/').str[0]

# Get assets from Planon
planon_assets = planon.UsrMEAsset.find()

# Create a set of Planon asset names using last 7 characters
planon_asset_names = {str(planon_asset.Code)[-7:] for planon_asset in planon_assets}
count_of_assets = len(planon_assets)
log.info(f"Total number of assets: {count_of_assets}")

# Create a DataFrame to store the results
result_df = pd.DataFrame({'Name': names_column, 'Parsed Name': parsed_names , 'Parsed IP address' : ip_address_column})

# Check if each parsed name has the exact parsed IP address
result_df['Present in Planon'] = result_df.apply(lambda row: 'Yes' if row['Parsed Name'] in planon_asset_names else 'No', axis=1)

# Write the results to a CSV file
result_df.to_csv('output/output_assets.csv', index=False)