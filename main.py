from pathlib import Path
import pandas as pd
from dateutil.relativedelta import relativedelta

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

def provincial_solar(province):
    import os

    solar_df = data_import.solar_power_import(solar_path)
    solar_df = solar_df[solar_df["State/Province"]==province]
    solar_df['index'] = range(0, len(solar_df))
    solar_df.to_excel("./results/" + province +"_solar_index.xlsx")

    # Tokens
    account_df = data_import.ninja_accounts_import(accounts_path)
    token_list = account_df.loc[:,"TOKEN"].tolist()

    # Parameters
    year = "2022"

    for i in range(0, len(solar_df)):
        print("iteration ", i,"/", len(solar_df)-1)
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
        
        if not os.path.exists("./results/china_solar/" + province + "/"):
            os.makedirs("./results/china_solar/" + province + "/")
        temp_data.to_excel("./results/china_solar/"+ province + "/" + province + "_"+ str(i) + ".xlsx")

if __name__ == "__main__":
    #solar_df = data_import.solar_power_import(solar_path)
    provincial_solar("Guizhou")
    """
    "Anhui"
    "Beijing"
    "Chongqing"
    "Fujian"
    "Gansu"
    "Guangdong"
    "Guangxi"
    "Guizhou"
    
    "Hainan"
    "Hebei"
    "Heilongjiang"
    "Henan"
    "Hubei"
    "Hunan"
    "Inner Mongolia"
    "Jiangsu"
    "Jiangxi"
    "Jilin"
    "Liaoning"
    "Ningxia"
    "Qinghai"
    "Shannxi"
    "Shandong"
    "Shanghai"
    "Shanxi"
    "Sichuan"
    "Tianjin"
    "Tibet"
    "Xinjiang"
    "Yunnan"
    "Zhejiang"
    """
    
    '''
    for i in range(0, len(solar_df)):
        print("file " + str(i))
        input_name = "gx_" + str(i) + ".xlsx"
        temp_df = pd.read_excel("./results/gx_solar/gx_" + str(i) + ".xlsx")
        temp_df.rename(columns={ temp_df.columns[0]: "time" }, inplace = True)
        
        temp_df["time"] = temp_df["time"].apply(lambda x:x + relativedelta(hours = 8))
        print(temp_df)
        
        output_name = "gx_" + str(i) + ".csv"
        temp_df.to_csv("./results/gx_solar_csv/" + output_name, index=False)
    '''
    
        