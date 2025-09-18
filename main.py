# Coding: utf-8
import pandas as pd
from dateutil.relativedelta import relativedelta
import os
import logging
import time
logging.basicConfig()

from utils import scraper_utils

if __name__ == "__main__":
    accounts_path = "./data/ninja_accounts.xlsx"
    solar_path = "./data/global_tracker/Global-Solar-Power-Tracker-February-2025.xlsx"
    wind_path = "./data/global_tracker/Global-Wind-Power-Tracker-February-2025.xlsx"
    result_base_path = "./result/"

    accounts_df = pd.read_excel(accounts_path)
    token_list = accounts_df.loc[:,"token"].tolist()
    
    solar_df_20M = pd.read_excel(solar_path, sheet_name="20 MW+")
    solar_df_less_20M = pd.read_excel(solar_path, sheet_name="1-20 MW")
    solar_df = pd.concat([solar_df_20M, solar_df_less_20M], ignore_index=True)
    solar_df = solar_df[solar_df["Country/Area"] == "China"]
    solar_df = solar_df[solar_df["State/Province"] == "Guangxi"]
    solar_df = solar_df[solar_df["Status"] == "operating"]
    solar_df["Capacity (kW)"] = solar_df["Capacity (MW)"] * 1000
    solar_df = solar_df.reset_index(drop=True)
    
    wind_df_above = pd.read_excel(wind_path, sheet_name="Data")
    wind_df_below = pd.read_excel(wind_path, sheet_name="Below Threshold")
    wind_df = pd.concat([wind_df_above, wind_df_below], ignore_index=True)
    wind_df = wind_df[wind_df["Country/Area"] == "China"]
    wind_df = wind_df[wind_df["State/Province"] == "Guangxi"]
    wind_df = wind_df[wind_df["Status"] == "operating"]
    wind_df["Capacity (kW)"] = wind_df["Capacity (MW)"] * 1000
    wind_df = wind_df.reset_index(drop=True)
    
    print(accounts_df)
    print(solar_df)
    print(wind_df)
    ########################################################################
    # Solar
    solar_result_save_path = result_base_path + "solar/Guangxi/"
    os.makedirs(solar_result_save_path, exist_ok=True)
    solar_df.to_excel(solar_result_save_path + "solar.xlsx", index=False)
    
    solar_ID_list = {f for f in os.listdir(solar_result_save_path) if os.path.isfile(os.path.join(solar_result_save_path, f))}
    solar_ID_list = [ID.rstrip(".xlsx") for ID in solar_ID_list]
    
    # Define the query parameters for solar
    system_loss = 0.1
    tracking = 0
    tilt = 35
    azim = 180
    year_solar = 2024
    dataset = 'merra2'

    # Start crawling data
    tk = 0
    for i, row in solar_df.iterrows():
        if tk == len(token_list):
            tk = 0

        print("row ", i, "/", len(solar_df)-1)
        print("tk ", tk, token_list[tk])

        coordinate = [row["Latitude"], row["Longitude"]]
        capacity = row["Capacity (kW)"]
        ID = row["GEM phase ID"]
        
        if str(ID) in solar_ID_list:
            print("skip ", ID)
            continue
        else:
            while True:
                temp_data, temp_metadata = scraper_utils.pv_request(
                    coordinates=coordinate,
                    year=year_solar,
                    token=token_list[tk],
                    capacity=capacity,
                    system_loss=system_loss,
                    tracking=tracking,
                    tilt=tilt,
                    azim=azim
                )
                
                if len(temp_data) == 0 or "no_response" in temp_data.columns:
                    tk += 1
                    if tk == len(token_list):
                        tk = 0  # wrap around if at end
                    continue  # retry with new token
                else:
                    tk += 1
                    print(temp_data)
                    temp_data.to_excel(solar_result_save_path + ID + ".xlsx", index=False)
                    time.sleep(1)  # wait before next request
                    break
               
    ########################################################################
    # Wind
    wind_result_save_path = result_base_path + "wind/Guangxi/"
    os.makedirs(wind_result_save_path, exist_ok=True)
    wind_df.to_excel(wind_result_save_path + "wind.xlsx", index=False)
    
    wind_ID_list = {f for f in os.listdir(wind_result_save_path) if os.path.isfile(os.path.join(wind_result_save_path, f))}
    wind_ID_list = [ID.rstrip(".xlsx") for ID in wind_ID_list]
    
    year_wind = 2024
    height = 100
    turbine_model = 'Vestas V80 2000'
    
    tk = 0
    for i, row in wind_df.iterrows():
        if tk == len(token_list):
            tk = 0

        print("row ", i, "/", len(wind_df)-1)
        print("tk ", tk, token_list[tk])

        coordinate = [row["Latitude"], row["Longitude"]]
        capacity = row["Capacity (kW)"]
        ID = row["GEM phase ID"]
        
        if str(ID) in wind_ID_list:
            print("skip ", ID)
            continue
        else:
            while True:
                temp_data, temp_metadata = scraper_utils.wind_request(coordinates=coordinate,
                                        year=year_wind,
                                        token=token_list[tk],
                                        capacity=capacity,
                                        height=height, 
                                        turbine=turbine_model)
                
                if len(temp_data) == 0 or "no_response" in temp_data.columns:
                    tk += 1
                    if tk == len(token_list):
                        tk = 0  # wrap around if at end
                    continue  # retry with new token
                else:
                    tk += 1
                    print(temp_data)
                    temp_data.to_excel(wind_result_save_path + ID + ".xlsx", index=False)
                    time.sleep(1)  # wait before next request
                    break   

    
        
    def time_zone_shift_solar(df_name, province):
        if not os.path.exists("./results/china_solar_csv/"):
            os.makedirs("./results/china_solar_csv/")
        
        if not os.path.exists("./results/china_solar_csv/" + province + "/"):
            os.makedirs("./results/china_solar_csv/" + province + "/")
            
        for i in range(0, len(df_name)):
            print("file " + str(i))
            temp_df = pd.read_excel("./results/china_solar/" + province + "/" + province + "_" + str(i) + ".xlsx")
            
            temp_df.rename(columns={ temp_df.columns[0]: "time" }, inplace = True)
            
            temp_df["time"] = temp_df["time"].apply(lambda x:x + relativedelta(hours = 8))
            print(temp_df)
            
            output_name =  province + "_" + str(i) + ".csv"
            temp_df.to_csv("./results/china_solar_csv/" + province + "/" + output_name, index=False)
        
        return None

    def time_zone_shift_wind(df_name, province):
        if not os.path.exists("./results/china_wind_csv/"):
            os.makedirs("./results/china_wind_csv/")
        
        if not os.path.exists("./results/china_wind_csv/" + province + "/"):
            os.makedirs("./results/china_wind_csv/" + province + "/")
            
        for i in range(0, len(df_name)):
            print("file " + str(i))
            temp_df = pd.read_excel("./results/china_wind/" + province + "/" + province + "_" + str(i) + ".xlsx")
            
            temp_df.rename(columns={ temp_df.columns[0]: "time" }, inplace = True)
            
            temp_df["time"] = temp_df["time"].apply(lambda x:x + relativedelta(hours = 8))
            print(temp_df)
            
            output_name =  province + "_" + str(i) + ".csv"
            temp_df.to_csv("./results/china_wind_csv/" + province + "/" + output_name, index=False)
        
        return None

  