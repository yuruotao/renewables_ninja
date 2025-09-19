import pandas as pd
import os


if __name__ == "__main__":
    province_list = ["Guangxi", "Guangdong", "Yunnan", "Hainan", "Guizhou"]
    wind_base_path = "./result/wind/"
    solar_base_path = "./result/solar/"
    wind_save_path = "./result/aggregate/wind/"
    solar_save_path = "./result/aggregate/solar/"
    os.makedirs(wind_save_path, exist_ok=True)
    os.makedirs(solar_save_path, exist_ok=True)
    
    for province in province_list:
        wind_path = wind_base_path + province + "/wind.xlsx"
        solar_path = solar_base_path + province + "/solar.xlsx"
        
        wind_df = pd.read_excel(wind_path)
        solar_df = pd.read_excel(solar_path)
        
        wind_df.to_excel(wind_save_path + province + "_wind.xlsx", index=False)
        solar_df.to_excel(solar_save_path + province + "_solar.xlsx", index=False)
        
        wind_file_list = {f for f in os.listdir(wind_base_path + province) if os.path.isfile(os.path.join(wind_base_path + province, f))}
        solar_file_list = {f for f in os.listdir(solar_base_path + province) if os.path.isfile(os.path.join(solar_base_path + province, f))}

        time_index = pd.date_range("2024-01-01 00:00:00", periods=8784, freq="H")
        
        wind_df_list = []
        for wind_file in wind_file_list:
            if wind_file == "wind.xlsx":
                continue
            temp_wind_df = pd.read_excel(wind_base_path + province + "/" + wind_file)
            ID = os.path.splitext(wind_file)[0]
            temp_wind_df.columns = [ID]
            
            wind_df = pd.concat([wind_df, temp_wind_df], ignore_index=True)
            wind_df_list.append(temp_wind_df)
        
        wind_data_df = pd.concat(wind_df_list, axis=1)
        wind_data_df.insert(0, "time", time_index)
        wind_data_df.to_excel(wind_save_path + province + "_wind_data.xlsx", index=False)
        
        solar_df_list = []
        for solar_file in solar_file_list:
            if solar_file == "solar.xlsx":
                continue
            temp_solar_df = pd.read_excel(solar_base_path + province + "/" + solar_file)
            ID = os.path.splitext(solar_file)[0]
            temp_solar_df.columns = [ID]
            
            solar_df = pd.concat([solar_df, temp_solar_df], ignore_index=True)
            solar_df_list.append(temp_solar_df)
        
        solar_data_df = pd.concat(solar_df_list, axis=1)
        solar_data_df.insert(0, "time", time_index)
        solar_data_df.to_excel(solar_save_path + province + "_solar_data.xlsx", index=False)
        
        