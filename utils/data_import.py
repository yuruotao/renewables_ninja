import pandas as pd




def province_name_to_lat_lon(xlsx_path):
    """Get the longitude and latitude from xlsx

    Args:
        xlsx_path (string): the xlsx file path pointing at the mass centers

    Returns:
        _type_: _description_
    """
    lat_lon_df = pd.read_excel(xlsx_path)
    
    lat_lon_df = lat_lon_df.rename(columns = {"lon":"LON", "lat":"LAT", "省":"PROVINCE"})
    lat_lon_df = lat_lon_df.astype({'LON': 'float','LAT': 'float', })
    lat_lon_df = lat_lon_df[["PAC", "NAME", "PROVINCE", "LON", "LAT"]]
    
    # Import the lat lon data and filter those in guangxi Province
    #coords_df = data_import.province_name_to_lat_lon(lat_lon_path)
    #gx_coords_df = coords_df[coords_df["PAC"].astype(str).str[:2].astype(int) == 45]
    #gx_coords_df = gx_coords_df.reset_index()
    
    return lat_lon_df

def solar_power_import(xlsx_path):
    """_summary_

    Args:
        xlsx_path (string): he xlsx file path pointing at the solar projects

    Returns:
        _type_: _description_
    """
    solar_param_df = pd.read_excel(xlsx_path, sheet_name="Data")
    #solar_param_df_1 = pd.read_excel(xlsx_path, sheet_name="Below Threashold")
    
    solar_param_df = solar_param_df[["Country", "State/Province", "Longitude", "Latitude", "Capacity (MW)", "Project Name"]]
    solar_param_df = solar_param_df[solar_param_df["Country"]=="China"]
    solar_param_df = solar_param_df[solar_param_df["State/Province"]=="Guangxi"]

    #solar_param_df = solar_param_df.astype({'LON': 'float','LAT': 'float', })
    return solar_param_df

def ninja_accounts_import(xlsx_path):
    account_df = pd.read_excel(xlsx_path)
    account_df = account_df.astype({'username': 'string','password': 'string','token': 'string', })
    account_df = account_df.rename(columns = {'username': 'USERNAME','password': 'PASSWORD','token': 'TOKEN',})
    
    return account_df


if __name__ == "__main__":
    print("ha")