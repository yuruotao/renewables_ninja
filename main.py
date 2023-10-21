from pathlib import Path
import pandas as pd

from utils import data_import
from utils import scraper_utils

import logging
logging.basicConfig()

current_path = str(Path())
input_data_path = current_path + "/data/model_input"
lat_lon_path = input_data_path + "/china_mass_center_2019.xlsx"
solar_path = input_data_path + "/Global-Solar-Power-Tracker.xlsx"
accounts_path = input_data_path + "/ninja_accounts.xlsx"

# Define the query parameters
system_loss = 0.1
tracking = False
tilt = 35
azim = 180
dataset = 'merra2'

def gx_solar():
    solar_df = data_import.solar_power_import(solar_path)
    solar_df['index'] = range(0, len(solar_df))
    solar_df.to_excel("./results/gx_solar_index.xlsx")

    # Tokens
    account_df = data_import.ninja_accounts_import(accounts_path)
    token_list = account_df.loc[:,"TOKEN"].tolist()

    # Parameters
    year = "2022"

    for i in range(202, len(solar_df)):
        print("iteration ", i)
        temp_df = solar_df[solar_df["index"]==i]
        coordinate=[]
        coordinate.append(temp_df["Latitude"])
        coordinate.append(temp_df["Longitude"])
        capacity=temp_df["Capacity (MW)"]
        temp_data, temp_metadata = scraper_utils.pv_request(coordinates=coordinate,
                                 year=year,
                                 token=token_list[4],
                                 capacity=capacity,
                                 system_loss= 0.1, 
                                 tracking= 0, 
                                 tilt= 35, 
                                 azim= 180)
        print(temp_data)
        temp_data.to_excel("./results/gx_solar/gx_"+ str(i) + ".xlsx")



if __name__ == "__main__":
    solar_df = data_import.solar_power_import(solar_path)
    for i in range(0, len(solar_df)):
        name = "gx_" + str(i) + ".xlsx"
        
    
        