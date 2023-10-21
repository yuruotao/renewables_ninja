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
#date_from = pd.to_datetime(2022, 1, 1)
#date_to = pd.to_datetime(2022,12,31)
capacity = 1.0
system_loss = 0.1
tracking = False
tilt = 35
azim = 180
dataset = 'merra2'


if __name__ == "__main__":

    
    # Import the accounts and generate clients
    #
    #client_list = []
    #for client_iter in range(len(accounts_df)):
    #    client = scraper_utils.Client.from_df(str(accounts_df["token"].iloc[client_iter]))
    #    client_list.append(client)
    #print(client_list)
    
    solar_df = data_import.solar_power_import(solar_path)
    solar_df['index'] = range(0, 0+len(solar_df))
    
    ### Set general parameters, fixed - These are constant in all processes
    coord_table = solar_df["index","longitude","latitude"]
    years = (2022)
    renewable = "pv"
    dep_capacity = solar_df["Capacity (MW)", "index"]

    ### Set variable parameters - Include whatever needs to vary over the processes
    ##################################################################################################
    # Tokens - 6 tokens/ accounts are needed per process for peak performance
    account_df = data_import.ninja_accounts_import(accounts_path)
    token_list = account_df.loc[:,"token"].tolist()

    #################################################################################################
    
    ### Parallelize processes over arg_list

    results = scraper_utils.ninja_parallel(coord_table=coord_table,
                            years= years, 
                            renewable= renewable, 
                            capacity_table= dep_capacity)
    
    ### Cautionary saving of results
    results.to_csv("./results/pv_test_south1.csv", index=False)
    print("Finished scraping.")
    
    