import pandas as pd




def province_name_to_lat_lon(xlsx_path):
    lat_lon_df = pd.read_excel(xlsx_path)
    
    lat_lon_df = lat_lon_df.rename(columns = {"lon":"LON", "lat":"LAT", "省":"PROVINCE"})
    lat_lon_df = lat_lon_df.astype({'LON': 'float','LAT': 'float', })
    lat_lon_df = lat_lon_df[["PAC", "NAME", "PROVINCE", "LON", "LAT"]]
    
    return lat_lon_df

def ninja_accounts_import(xlsx_path):
    account_df = pd.read_excel(xlsx_path)
    account_df = account_df.astype({'username': 'string','password': 'string','token': 'string', })
    account_df = account_df.rename(columns = {'username': 'USERNAME','password': 'PASSWORD','token': 'TOKEN',})
    
    return account_df


if __name__ == "__main__":
    province_name_to_lat_lon()