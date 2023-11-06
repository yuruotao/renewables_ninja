from pathlib import Path
import pandas as pd
from dateutil.relativedelta import relativedelta
import os

from utils import data_import
from utils import scraper_utils

import logging
logging.basicConfig()

current_path = str(Path())
input_data_path = current_path + "/data/model_input"
lat_lon_path = input_data_path + "/china_mass_center_2019.xlsx"
solar_path = input_data_path + "/Global-Solar-Power-Tracker.xlsx"
accounts_path = input_data_path + "/ninja_accounts.xlsx"
wind_path = input_data_path + "/Global-Wind-Power-Tracker.xlsx"

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

    for i in range(46, 47):
        #len(solar_df)
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
        temp_data.to_excel("./results/china_solar/gx_solar/gx_"+ str(i) + ".xlsx")

def provincial_solar(province):
    import os

    solar_df = data_import.solar_power_import(solar_path)
    solar_df = solar_df[solar_df["State/Province"]==province]
    solar_df['index'] = range(0, len(solar_df))
    solar_df.to_excel("./results/solar_index/" + province +"_solar_index.xlsx")

    # Tokens
    account_df = data_import.ninja_accounts_import(accounts_path)
    token_list = account_df.loc[:,"TOKEN"].tolist()

    # Parameters
    year = "2022"
    tk = 0


    for i in range(0, len(solar_df)):
        if tk == (len(token_list)):
            tk = 0
        
        print("iteration ", i,"/", len(solar_df)-1)
        print("tk ", tk, token_list[tk])
        temp_df = solar_df[solar_df["index"]==i]
        coordinate=[]
        coordinate.append(temp_df["Latitude"])
        coordinate.append(temp_df["Longitude"])
        capacity=temp_df["Capacity (MW)"]
        temp_data, temp_metadata = scraper_utils.pv_request(coordinates=coordinate,
                                 year=year,
                                 token=token_list[tk],
                                 capacity=capacity,
                                 system_loss= 0.1, 
                                 tracking= 0, 
                                 tilt= 35, 
                                 azim= 180)
        print(temp_data)
        tk =tk + 1
        
        if not os.path.exists("./results/china_solar/" + province + "/"):
            os.makedirs("./results/china_solar/" + province + "/")
        temp_data.to_excel("./results/china_solar/"+ province + "/" + province + "_"+ str(i) + ".xlsx")

def provincial_wind(province):
    import os

    wind_df = data_import.wind_power_import(wind_path)
    wind_df = wind_df[wind_df["State/Province"]==province]
    wind_df['index'] = range(0, len(wind_df))
    wind_df.to_excel("./results/wind_index/" + province +"_wind_index.xlsx")

    # Tokens
    account_df = data_import.ninja_accounts_import(accounts_path)
    token_list = account_df.loc[:,"TOKEN"].tolist()

    # Parameters
    year = "2022"

    tk = 0
    
    for i in range(232, len(wind_df)):
        if tk == (len(token_list)):
            tk = 0
        
        print("iteration ", i,"/", len(wind_df)-1)
        print("tk ", tk, token_list[tk])
        temp_df = wind_df[wind_df["index"]==i]
        coordinate=[]
        coordinate.append(temp_df["Latitude"])
        coordinate.append(temp_df["Longitude"])
        capacity=temp_df["Capacity (MW)"]
        temp_data, temp_metadata = scraper_utils.wind_request(coordinates=coordinate,
                                 year=year,
                                 token=token_list[tk],
                                 capacity=capacity,
                                 height= 100, 
                                 turbine= 'Vestas V80 2000')
        print(temp_data)
        tk =tk + 1
        
        if not os.path.exists("./results/china_wind/" + province + "/"):
            os.makedirs("./results/china_wind/" + province + "/")
        temp_data.to_excel("./results/china_wind/"+ province + "/" + province + "_"+ str(i) + ".xlsx")

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

if __name__ == "__main__":
    province = "Hebei"
    #provincial_solar("Hubei")
    #provincial_solar(province)
    #solar_df = data_import.solar_power_import(solar_path)
    #solar_df_province = solar_df[solar_df["State/Province"]== province]
    #solar_df_province['index'] = range(0, len(solar_df_province))
    #time_zone_shift_solar(solar_df_province, province)
    
    provincial_wind(province)
    #wind_df = data_import.wind_power_import(wind_path)
    #wind_df_province = wind_df[wind_df["State/Province"]== province]
    #wind_df_province['index'] = range(0, len(wind_df_province))
    #time_zone_shift_wind(wind_df_province, province)
    

    
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
    

    
        