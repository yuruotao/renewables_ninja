from pathlib import Path
import pandas as pd
import os as os
import numpy as np
from multiprocessing import Pool
from functools import partial

from utils import data_import
from utils import scraper_utils
import utils.scraper_utils as rn

current_path = str(Path())
input_data_path = current_path + "/data/model_input"
lat_lon_path = input_data_path + "/china_mass_center_2019.xlsx"

### Baseline function to parallelize
###################################################################################################
def ninja_parallel(specs, coord_table, years, renewable, capacity_table, 
                       burst_limit=6, sustained_limit=50, unit_divider=1, source_type=""):
    """
    Args:
        coord_table (pd.DataFrame): _description_
        years (tuple): _description_
        renewable (string): _description_
        tokens (list): _description_
        func_params (dict): _description_
        capacity_table (pd.DataFrame): _description_
        burst_limit (int, optional): _description_. Defaults to 6.
        sustained_limit (int, optional): _description_. Defaults to 50.
        unit_divider (int, optional): _description_. Defaults to 1.
        source_type (str, optional): _description_. Defaults to "".
    """
    
    ## Separate relevant arguments - 
    ## this should correspond in possition to the list supplied to the function lateron
    tokens = specs[0]
    func_params = specs[1]


    ## Set func_param to default if they are missing
    default_params = {"capacity": 1.0,
                      "system_loss": 0.1,
                      "tracking": 0,
                      "tilt": 35,
                      "azim": 180,
                      "height": 100, 
                      "turbine": 'Vestas V80 2000'}

    for param in default_params.keys():
        if np.invert(param in func_params.keys()):
            func_params[param] = default_params[param]

    ## Create one massive param_table with year included (modify prep_paramtable)
    param_table = rn.prep_param_table(coord_table=coord_table, renewable=renewable, 
                                   capacity=[func_params["capacity"]],
                                   system_loss= [func_params["system_loss"]],
                                   tracking= [func_params["tracking"]],
                                   azimuth= [func_params["azim"]],
                                   tilt= [func_params["tilt"]],
                                   height= [func_params["height"]],
                                   turbine= [func_params["turbine"]])

    ## Run flexreq on this table with a chaining of tokens (modify flexreq)
    ninja_table = rn.ninja_flexreq(param_table=param_table, renewable=renewable, 
                                years=years, tokens=tokens, burst_limit=burst_limit,
                                sustained_limit=sustained_limit)
    
    ## Aggreagte over flexreq as usual
    ninja_table = rn.ninja_aggregation(ninja_table=ninja_table, renewable=renewable,
                                    capacity_table=capacity_table, unit_divider=unit_divider,
                                    source_type=source_type)    
    return(ninja_table)
###################################################################################################


if __name__ == "__main__":
    #data_import.province_name_to_lat_lon(lat_lon_path)
    
    ### Set general parameters, fixed - These are constant in all processes
    coord_table = pd.read_excel(r"inputs\VRE profiles locations.xlsx", sheet_name="PV")
    years = (2000,2019)
    renewable = "pv"
    dep_capacity = pd.read_excel(r"inputs\Capacities per department.xlsx", sheet_name="Capacities per department")

    ### Set variable parameters - Include whatever needs to vary over the processes
    ##################################################################################################
    # Tokens - 6 tokens/ accounts are needed per process for peak performance
    account_df = pd.read_csv("ninja_accounts.csv") #### Use an account file like template
    token_list =[account_df.loc[:5,"token"].tolist(),
                 account_df.loc[6:11,"token"].tolist(),
                 account_df.loc[12:,"token"].tolist()]
    # Function parameters
    param_list = [{"tilt": 35, "azim": 180, "capacity": 1000000},
                  {"tilt": 10, "azim": 90, "capacity": 1000000},
                  {"tilt": 10, "azim": 270, "capacity": 1000000}]    
    # Bring together in list - careful with position of lists
    arg_list = list(zip(token_list, param_list))
    #################################################################################################
    
    ### Parallelize processes over arg_list
    p = Pool(processes=3) #Choose number of processes according to number of available cores
    results = p.map(partial(ninja_parallel, coord_table=coord_table,
                            years= years, renewable= renewable, 
                            capacity_table= dep_capacity), #fixed params in the partial()
                    arg_list) #process-variable params in this list
    p.terminate()
    p.join()
    
    ### Cautionary saving of results
    results[0].to_csv("pv_test_south1.csv", index=False)
    results[1].to_csv("pv_test_east1.csv", index=False)
    results[2].to_csv("pv_test_west1.csv", index=False)
    print("Finished scraping.")  
    
    
    