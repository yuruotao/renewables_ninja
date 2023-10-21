from pathlib import Path
import pandas as pd

from utils import data_import
from utils import scraper_utils

import logging
logging.basicConfig()

current_path = str(Path())
input_data_path = current_path + "/data/model_input"
lat_lon_path = input_data_path + "/china_mass_center_2019.xlsx"
accounts_path = input_data_path + "/ninja_accounts.xlsx"

# Define the query parameters
#date_from = pd.to_datetime(2022, 1, 1)
#date_to = pd.to_datetime(2022,12,31)
capacity = 1.0
system_loss = 0.1
tracking = False
tilt = 35
azim = 180
dataset = 'merra2'


if __name__ == "__main__":
    # Import the lat lon data and filter those in guangxi Province
    coords_df = data_import.province_name_to_lat_lon(lat_lon_path)
    gx_coords_df = coords_df[coords_df["PAC"].astype(str).str[:2].astype(int) == 45]
    gx_coords_df = gx_coords_df.reset_index()
    
    # Import the accounts and generate clients
    accounts_df = data_import.ninja_accounts_import(accounts_path)
    client_list = []
    for client_iter in range(len(accounts_df)):
        client = scraper_utils.Client.from_df(str(accounts_df["token"].iloc[client_iter]))
        client_list.append(client)
    print(client_list)
    

    
    
    