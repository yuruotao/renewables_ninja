import requests
import pandas as pd
import json
from time import sleep
import numpy as np

### Define request functions for single site-locations

def pv_request(coordinates, year, token=None, capacity=1.0,
               system_loss=0.1, tracking=0, tilt=35, azim=180):
    """
    Get a single time series for Photovoltaics 
    Retrieve a series of PV production for the specification indicated.

    Args:
        coordinates (tuple): Coordinates as floats for location.
        year (string): Year for data retrieval.
        token (string, optional): String token for increased access limits. Defaults to None with limit 5 per day
        capacity (float, optional): Installed capacity at location. Defaults to 1.0.
        system_loss (float, optional): Loss of energy within the system. Defaults to 0.1.
        tracking (int, optional): Indicator if panels conduct tracking of sun. Defaults to 0.
        tilt (int, optional): Degree of tilt for the panels. Defaults to 35.
        azim (int, optional): Degree of azimuth for the the panels. Defaults to 180.
    """
    year = str(year)
    
    #Set url base and add pv indicator
    api_base = 'https://www.renewables.ninja/api/'
    url = api_base + 'data/pv'
    
    s = requests.session()
    # Send token header with each request
    if pd.notna(token):
        s.headers = {'Authorization': 'Token ' + token}

    ##End function if coordinates are NA
    if all(np.isnan(coordinates)):
        return(pd.DataFrame(columns = ["invalid_coordinates"]), dict())
    
    ##Specify characteristics of the api call
    args = {
        'lat': coordinates[0],
        'lon': coordinates[1],
        'date_from': year+'-01-01',
        'date_to': year+'-12-31',
        'dataset': 'merra2',
        'capacity': capacity,
        'system_loss': system_loss,
        'tracking': tracking,
        'tilt': tilt,
        'azim': azim,
        'format': 'json'
    }
    
    #Execute api request
    r = s.get(url, params=args)

    # Parse JSON to get a pandas.DataFrame of data and dict of metadata
    try:    
        parsed_response = json.loads(r.text)
    except Exception as e:
        print("Error", e)
        return(pd.DataFrame(columns = ["no_response"]), dict())

    data = pd.read_json(json.dumps(parsed_response['data']), orient='index')
    metadata = parsed_response['metadata']
    print("Finished")
    return data, metadata

def wind_request(coordinates, year, token= None, capacity= 1.0,
                 height= 100, turbine= 'Vestas V80 2000'):
    """
    Get a single time series for Wind turbines 
    Retrieve a series of wind turbine production for the specification indicated.
    
    Args:
        coordinates (tuple): Coordinates as floats for location.
        year (string): Year for data retrieval.
        token (string, optional): String token for increased access limits. Defaults to None with limit 5 per day
        capacity (float, optional): Installed capacity at location. Defaults to 1.0.
        height (int, optional): Height of turbine installed. Defaults to 100.
        turbine (str, optional): Model of turbine installed. Defaults to 'Vestas V80 2000'.
    """
    year = str(year)
    #Set url base and add wind indicator
    api_base = 'https://www.renewables.ninja/api/'
    url = api_base + 'data/wind'
    
    s = requests.session()
    # Send token header with each request
    if pd.notna(token):
        s.headers = {'Authorization': 'Token ' + token}
    
    ##End function if coordinates are NA
    if all(np.isnan(coordinates)):
        return(pd.DataFrame(columns = ["invalid_coordinates"]), dict())
    
    ##Specify characteristics of the api call
    args = {
        'lat': coordinates[0],
        'lon': coordinates[1],
        'date_from': year+'-01-01',
        'date_to': year+'-12-31',
        'dataset': 'merra2',
        'capacity': capacity,
        'height': height,
        'turbine': turbine,
        'format': 'json'
    }
    #Execute api request
    r = s.get(url, params=args)

    # Parse JSON to get a pandas.DataFrame of data and dict of metadata
    try:
        parsed_response = json.loads(r.text)
    except json.JSONDecodeError:
        #print("Decode error")
        return(pd.DataFrame(columns = ["no_response"]), dict())

    data = pd.read_json(json.dumps(parsed_response['data']), orient='index')
    metadata = parsed_response['metadata']
    
    return(data, metadata)

### Define helper functions for loop

def prep_coord_list(coord_table):
    """
    Prepare a list of coordinates and department numbers

    Args:
        coord_table (pd.DataFrame): Table of coordinates and department numbers to process.
    """
    
    index_list = coord_table["index"].astype(str).to_list()
    
    table = coord_table.assign(
        Latitude_init= lambda x: x["Latitude"].astype(str),
        Latitude= lambda x: x["Latitude_init"].replace("-", "nan").astype(float),
        Longitude_init= lambda x: x["Longitude"].astype(str),
        Longitude= lambda x: x["Longitude_init"].replace("-", "nan").astype(float))
    coord_list = list(zip(table["Latitude"],
                          table["Longitude"]))
    return(coord_list, index_list)

def prep_param_table(coord_table, renewable, capacity= [1.0], system_loss=[0.1], 
                     tracking=[0], tilt=[35], azimuth=[180], height=[100],
                     turbine=['Vestas V80 2000'], save=""):
    """
    Generate table of parameter settings.
    Generate a table of parameter settings according to the intended specifications.

    Args:
        coord_table (pd.DataFrame): Table of coordinates and department numbers to process.
        renewable (string): String indicating what generation to use. "pv" for photovolatics, "onshore" for onshore wind turbines.
        capacity (list, optional): List of installed capacity at location. Defaults to [1.0].
        system_loss (list, optional): List of loss of energy within the system. Defaults to [0.1].
        tracking (list, optional): List of indicators if panels conduct tracking of sun. Defaults to [0].
        tilt (list, optional): List of degrees of tilt for the panels. Defaults to [35].
        azimuth (list, optional): List of degrees of azimuth for the the panels. Defaults to [180].
        height (list, optional): List of height of turbine installed. Defaults to [100].
        turbine (list, optional): List of model of turbine installed. Defaults to ['Vestas V80 2000'].
        save (str, optional): Path string for saving the finished table. Defaults to "", which implies no saving.
    """
    
    ## Replace invalid coordinates
    coord_table = coord_table.assign(
        Latitude= lambda x: x["Latitude"].replace("-", "nan").astype(float),
        Longitude= lambda x: x["Longitude"].replace("-", "nan").astype(float))
    
    ## Remove rows with invalid coordinates from request series
    param_cond = (pd.notna(coord_table["Latitude"]) & pd.notna(coord_table["Longitude"]))
    param_table = coord_table.loc[param_cond]
    param_table.reset_index(drop=True, inplace=True)
    
    if renewable == "pv":
        func_params = {"capacity": capacity,
                       "system_loss": system_loss,
                       "tracking": tracking,
                       "azimuth": azimuth,
                       "tilt": tilt}
           
    elif renewable == "onshore":
        func_params = {"capacity": capacity,
                       "system_loss": system_loss,
                       "height": height,
                       "turbine": turbine}
            
    for param in func_params.keys():
        param_spec = func_params[param]
        
        if not(isinstance(param_spec, list)):
            param_spec = [param_spec] 
            
        if len(param_spec) == 1:
            param_table = param_table.assign(**{param: param_spec[0]})
        else:
            param_spec = pd.Series(param_spec)
            param_spec = param_spec.loc[param_cond]
            param_table[param] = param_spec 
                      
    if save != "":
        param_table.to_csv(save, index=False)
           
    return(param_table)

def limit_keeper(iterstart, iterend, limit_dict, burst_limit=6, sustained_limit=50):
    """
    Maintains limits of the API
    Ensures that the calls to the API within a loop of requests do not exceed the minute
    limit or hourly limit.

    Args:
        iterstart (datetime): Start time of iteration.
        iterend (datetime): End time of iteration.
        limit_dict (dict): Dictionary to record burst_timer, burst_count, sustained_timer, sustained_count
            - burst_timer (int): Count of seconds elapsed during in a minute.
            - burst_count (int): Count of requests used in last minute.
            - sustained_timer (int): Count of seconds elapsed since start
            - sustained_count (int): Count of requests used in last hour.
        burst_limit (int, optional): Limit of requests per minute. Defaults to 6.
        sustained_limit (int, optional): limit of requests per hour. Defaults to 50.
    """
    limit_dict["burst_timer"] += (iterend - iterstart).seconds
    limit_dict["burst_count"] += 1
   
    limit_dict["sustained_timer"] += (iterend - iterstart).seconds
    limit_dict["sustained_count"] += 1
    print("Sustained timer: "+str(limit_dict["sustained_timer"]))
    print("Sustained count: "+str(limit_dict["sustained_count"]))
        
    #Control time elapsed and iterations run for the minute
    if limit_dict["burst_timer"] > 60:
        limit_dict["burst_count"] = 0
        limit_dict["burst_timer"] = 0
    elif limit_dict["burst_count"] >= burst_limit:
        print("Sleeping: "+str(60 - limit_dict["burst_timer"]))
        sleep(60 - limit_dict["burst_timer"])
        limit_dict["sustained_timer"] += (60 - limit_dict["burst_timer"]) 
        limit_dict["burst_count"] = 0
        limit_dict["burst_timer"] = 0
            
    #Control time elapsed and iterations run for the hour
    if limit_dict["sustained_count"] >= sustained_limit:
        print("Sleeping: "+str(3600 - limit_dict["sustained_timer"]))
        sleep(3600 - limit_dict["sustained_timer"])
        limit_dict["sustained_count"] = 0
        limit_dict["sustained_timer"] = 0
    
    return(limit_dict)

def update_tokens(token, token_df):
    """
    Update an expired token according to available token regen times
    
    This function accepts a token and token table and returns a new token for which the
    regeneration time is minimal. It then sets the new regeneration time of that token 
    an hour ahead.

    Args:
        token (string): Currently active token.
        token_df (pd.DataFrame): Table of tokens with their regeneration times recorded.
    """
    
    new_regen = pd.Timestamp.now() + pd.Timedelta(1, unit= "hours")
        
    token = token_df.loc[
        token_df["regen_time"].min() == token_df["regen_time"],
        "tokens"].tolist()[0]
    
    token_df.loc[token_df["tokens"] == token, "regen_time"] = new_regen
    
    return(token, token_df)

def chain_limit_keeper(token, token_df, iterstart, iterend, limit_dict, burst_limit=6,
                       sustained_limit=50):
    """
    Maintains limits of the API with chained tokens
    
    Ensures that the calls to the API within a loop of requests do not exceed the minute
    limit or hourly limit. Switches in next token from list if limit is reached. Will wait
    for limit to regenerate.

    Args:
        token (string): Currently active token.
        token_df (pd.DataFrame): Table of tokens with their regeneration times recorded.
        iterstart (datetime): Start time of iteration.
        iterend (datetime): End time of iteration.
        limit_dict (dict): Dictionary to record burst_timer, burst_count, sustained_timer, sustained_count
            - burst_timer (int): Count of seconds elapsed during in a minute.
            - burst_count (int): Count of requests used in last minute.
            - sustained_timer (int): Count of seconds elapsed since start
            - sustained_count (int): Count of requests used in last hour.
        burst_limit (int, optional): Limit of requests per minute. Defaults to 6.
        sustained_limit (int, optional): limit of requests per hour. Defaults to 50.
    """
    limit_dict["burst_timer"] += (iterend - iterstart).seconds
    limit_dict["burst_count"] += 1
        
    limit_dict["sustained_timer"] += (iterend - iterstart).seconds
    limit_dict["sustained_count"] += 1
    print("Sustained timer: "+str(limit_dict["sustained_timer"]))
    print("Sustained count: "+str(limit_dict["sustained_count"]))
        
    #Control time elapsed and iterations run for the minute
    if limit_dict["burst_timer"] > 60:
        limit_dict["burst_count"] = 0
        limit_dict["burst_timer"] = 0
    elif limit_dict["burst_count"] >= burst_limit:
        print("Sleeping: "+str(60 - limit_dict["burst_timer"]))
        sleep(60 - limit_dict["burst_timer"])
        limit_dict["sustained_timer"] += (60 - limit_dict["burst_timer"]) 
        limit_dict["burst_count"] = 0
        limit_dict["burst_timer"] = 0
            
    #Control time elapsed and iterations run for the hour
    if limit_dict["sustained_count"] >= sustained_limit:
        if all(token_df["regen_time"] > pd.Timestamp.now()):
            resume_time = token_df.loc[
                token_df["regen_time"].min() == token_df["regen_time"], "regen_time"].tolist()[0]
            wait_time = (resume_time - pd.Timestamp.now()).seconds
            print("Sleeping: "+str(wait_time))
            sleep(wait_time)
     
        token, token_df = update_tokens(token, token_df)
        print("Sleeping 120 sec for overload prevention.")
        sleep(60*2)
        limit_dict["sustained_count"] = 0
        limit_dict["sustained_timer"] = 0
        print("Shift in token: "+token)
            
    return(token, token_df, limit_dict)

### Define requests loop

def ninja_flexreq(param_table, renewable, years, tokens=[], burst_limit=6, 
                  sustained_limit=4):
    """Run loop of requests over flexible parameter set
    
    Run a loop of requests over a set of completely flexible parameter settings (possibly one per coordinate set).

    Args:
        param_table (pd.DataFrame): Table of parameter settings.
        renewable (string): String indicating what generation to use. "pv" for photovolatics, "onshore" for onshore wind turbines.
        years (int or tuple of ints): Years for data retrieval (inclusive).
        tokens (list, optional): List of tokens to be used. Defaults to [].
        burst_limit (int, optional): Limit of requests per minute. Defaults to 6.
        sustained_limit (int, optional): limit of requests per hour. Defaults to 50.
        """
    print(pd.Timestamp.now())
    ## Defin limit_dict for API request limit tracking
    limit_dict = {"burst_timer": 0,
                  "burst_count": 0,
                  "sustained_timer": 0,
                  "sustained_count": 0}
    
    ## Process years input 
    if isinstance(years, tuple):
        year_seq = np.arange(years[0], years[1]+1, 1).astype(str)

        year_df = pd.DataFrame({"year": year_seq,
                                "renew": renewable,
                                "year_hours": 8760})
        year_df.loc[(year_df["year"].astype(int) % 4) == 0, "year_hours"] = 8784
        param_table = param_table.assign(renew = renewable)
        param_table = param_table.merge(year_df[["year","renew"]], on="renew",
                                        how="outer")
        param_table.pop("renew")
        param_table.reset_index(drop=True, inplace=False) 
    else:
        year = str(years)

    ## Generate list of coordinates and department numbers
    coord_list, index_list = prep_coord_list(param_table)
    capacity_list = param_table["capacity"]
    if renewable == "pv":
        azim_list = param_table["azimuth"]
        tilt_list = param_table["tilt"]
        tracking_list = param_table["tracking"]
        system_loss_list = param_table["system_loss"]
    elif renewable == "onshore":
        height_list = param_table["height"]
        turbine_list = param_table["turbine"] 
    
    ## Transform input "tokens" into list if not one
    if not(isinstance(tokens, list)):
        tokens = [tokens]
    
    ## Adapt token processing/ sustained limit based on length of tokens list
    if len(tokens) == 1:
        sustained_limit = 50
        token = tokens[0]
    elif len(tokens) > 1:
        sustained_limit = 50
        token_df = pd.DataFrame({"tokens": tokens,
                                "regen_time": pd.to_datetime("2020-01-01")})
        token, token_df = update_tokens(token="", token_df= token_df)
        print("Shift in token: "+token)
        
    ## Initialise loop dataframe
    data_total = pd.DataFrame(columns= ["time_step"])
    id = 0

    #Run loop of requests
    while id < len(coord_list):

        #Measure time of iteration
        iterstart = pd.Timestamp.now()
        if isinstance(years, tuple):
            print("Processing "+str(coord_list[id])+", "+str(index_list[id])+", "+param_table.loc[id,"year"])
        else:
            print("Processing "+str(coord_list[id])+", "+str(index_list[id]))
        
        #Run requests for current id
        coord = coord_list[id]
        
        ## adapt year variable if broadcasting over years
        if isinstance(years, tuple):
            year = param_table.loc[id,"year"]

        if renewable == "pv":
            data, meta_data = pv_request(coordinates=coord, year=year, token=token, 
                                         capacity=capacity_list[id],
                                         system_loss=system_loss_list[id],
                                         tracking=tracking_list[id],
                                         tilt=tilt_list[id],
                                         azim=azim_list[id])
        elif renewable == "onshore":
            data, meta_data = wind_request(coordinates=coord, year=year, token=token,
                                           capacity=capacity_list[id],
                                           height=height_list[id],
                                           turbine=turbine_list[id])
        
        if data.columns[0] == "invalid_coordinates":
            ## Increase id by 1 to advance loop
            id += 1
        elif data.columns[0] == "no_response":
            ## Print error and wait to rerun
            print("JSON parsing failed: retrying in 10s")
            sleep(10)
            
            ## Running limit maintenance
            iterend = pd.Timestamp.now()
            if len(tokens) <= 1:
                limit_dict = limit_keeper(iterstart, iterend, limit_dict, 
                                          burst_limit=burst_limit, sustained_limit=sustained_limit) 
            else:
                token, token_df, limit_dict = chain_limit_keeper(token, token_df, iterstart, iterend,
                                                                 limit_dict, burst_limit=burst_limit,
                                                                 sustained_limit=sustained_limit)
            
        else: ## Create time_step variable and rename electricity
            if isinstance(years, tuple): # if requests are broadcasted over years
                #Create time step variable
                year_id = np.where(year_seq==year)[0][0]#+1
                time_step_start = np.array(year_df.loc[:year_id,"year_hours"])[:-1].sum()
                time_step_end = time_step_start+data.shape[0]
                data["time_step"] = np.arange(time_step_start,time_step_end,1)           
                #Rename column with department index number
                data.rename(columns={"electricity": "electricity"+index_list[id]}, 
                            inplace= True) 
                
                ## Merge into main dataset
                data_total = data_total.merge(data[["time_step","electricity"+index_list[id]]],
                                              on="time_step", how= "outer", suffixes=("","_new"))
                
                ## Fill in NA
                col_list = [col for col in data_total.columns if col.endswith('_new')]
                if len(col_list) > 0:
                    data_total["electricity"+index_list[id]].fillna(data_total[col_list].iloc[:,0],
                                                                  inplace=True)
                    data_total.pop(col_list[0])             
                
            else: # if requests are not broadcasted over years
                #Create time step variable
                data["time_step"] = np.arange(0, data.shape[0],1)
                #Rename column with department index number
                data.rename(columns={"electricity": "electricity"+index_list[id]}, 
                            inplace= True)
                ## Merge into main dataset
                data_total = data_total.merge(data[["time_step","electricity"+index_list[id]]],
                                              on="time_step", how= "outer")

            ## Running limit maintenance
            iterend = pd.Timestamp.now()
            if len(tokens) <= 1:
                limit_dict = limit_keeper(iterstart, iterend, limit_dict, 
                                          burst_limit=burst_limit, sustained_limit=sustained_limit) 
            else:
                token, token_df, limit_dict = chain_limit_keeper(token, token_df, iterstart, iterend,
                                                                 limit_dict, burst_limit=burst_limit,
                                                                 sustained_limit=sustained_limit)  
            ## Increase id by 1 to advance loop
            id +=1
            
    ## Reset index for proper formatting
    data_total.reset_index(drop=True, inplace=False) 
     
    return(data_total)

def ninja_basereq(coord_table, renewable, years, tokens=[], 
                  func_params={"capacity": 1.0,
                               "system_loss": 0.1,
                               "tracking": 0,
                               "tilt": 35,
                               "azim": 180,
                               "height": 100,
                               "turbine": 'Vestas V80 2000'},
                  burst_limit=6, sustained_limit=50):
    """
    Run loop of requests for a single parameter set
    Run a loop of requests over a single set of fixed parameters

    Args:
        coord_table (_type_): _description_
        renewable (string): String indicating what generation to use. "pv" for photovolatics, "onshore" for onshore wind turbines.
        years (int or tuple of ints): Years for data retrieval (inclusive).
        tokens (list, optional): List of tokens to be used. Defaults to [].
        burst_limit (int, optional): Limit of requests per minute. Defaults to 6.
        sustained_limit (int, optional): limit of requests per hour. Defaults to 50.
    """
 
    ## Set default parameters
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

    param_table = prep_param_table(coord_table=coord_table, renewable=renewable, 
                                   capacity=[func_params["capacity"]],
                                   system_loss= [func_params["system_loss"]],
                                   tracking= [func_params["tracking"]],
                                   azimuth= [func_params["azim"]],
                                   tilt= [func_params["tilt"]],
                                   height= [func_params["height"]],
                                   turbine= [func_params["turbine"]])
    
    data_total = ninja_flexreq(param_table=param_table, renewable=renewable, years=years,
                               tokens=tokens, burst_limit=burst_limit, sustained_limit=sustained_limit)
                 
    return(data_total)

### Define Aggregation function
def ninja_aggregation(ninja_table, renewable, capacity_table, unit_divider= 1, 
                      source_type= ""):
    """
    Aggrate results from requests function
    Computes a weighted average over power series with a list of capacities.

    Args:
        ninja_table (pd.DataFrame): Table of time steps and regional power generation.
        renewable (string): String indicating what generation to use. "pv" for photovolatics, "onshore" for onshore wind turbines.
        capacity_table (pd.DataFrame): Table of generation capacity per region.
        unit_divider (int): Indicator by what factor the aggregation inputs should be divided (unit conversion). Defaults to 1.
        source_type (str, optional): Name of power generation source. Defaults to "" for non-inclusion.
    """
    
    dep_capacity = capacity_table.loc[capacity_table["VRE"] == renewable,
                                      ["department","capacity"]]
    dep_capacity.sort_values(by="department", inplace=True)
    
    capacities = dep_capacity.loc[
        dep_capacity["capacity"] != 0, "capacity"]
    capacities.reset_index(drop=True,inplace=True)
 
    reg_electricity = ninja_table.loc[:,ninja_table.columns.str.startswith('electr')]
    reg_electricity = reg_electricity/unit_divider
    print(reg_electricity.shape)
    print(len(capacities))
    ##dep_capacity must have same length 
    ninja_output = ninja_table[["time_step"]].copy()
    ninja_output["electricity"] = np.average(reg_electricity, axis=1, 
                                             weights= capacities)
        
    if source_type != "":
        ninja_output= ninja_output.assign(
            source_type= lambda x: source_type)

    return(ninja_output)

# Baseline function to parallelize
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
    param_table = prep_param_table(coord_table=coord_table, renewable=renewable, 
                                   capacity=[func_params["capacity"]],
                                   system_loss= [func_params["system_loss"]],
                                   tracking= [func_params["tracking"]],
                                   azimuth= [func_params["azim"]],
                                   tilt= [func_params["tilt"]],
                                   height= [func_params["height"]],
                                   turbine= [func_params["turbine"]])

    ## Run flexreq on this table with a chaining of tokens (modify flexreq)
    ninja_table = ninja_flexreq(param_table=param_table, renewable=renewable, 
                                years=years, tokens=tokens, burst_limit=burst_limit,
                                sustained_limit=sustained_limit)
     
    return(ninja_table)

if __name__ == "__main__":
    accounts_path = "./data/ninja_accounts.xlsx"
    solar_path = "./data/global_tracker/Global-Solar-Power-Tracker-February-2025.xlsx"
    wind_path = "./data/global_tracker/Global-Wind-Power-Tracker-February-2025.xlsx"

    accounts_df = pd.read_excel(accounts_path)
    token_list = accounts_df.loc[:,"token"].tolist()
    
    solar_df_20M = pd.read_excel(solar_path, sheet_name="20 MW+")
    solar_df_less_20M = pd.read_excel(solar_path, sheet_name="1-20 MW")
    solar_df = pd.concat([solar_df_20M, solar_df_less_20M], ignore_index=True)
    
    wind_df_above = pd.read_excel(wind_path, sheet_name="Data")
    wind_df_below = pd.read_excel(wind_path, sheet_name="Below Threshold")
    wind_df = pd.concat([wind_df_above, wind_df_below], ignore_index=True)
    
    print(accounts_df)
    print(solar_df)
    print(wind_df)
    
    # Define the query parameters for solar
    system_loss = 0.1
    tracking = False
    tilt = 35
    azim = 180
    year_solar = 2022
    dataset = 'merra2'
    
    # Define the query parameters for wind
    year_wind = 2022
    height = 100
    turbine_model = 'Vestas V80 2000'
    
    # Start crawling data
    tk = 0

    for i, row in solar_df.iterrows():
        if tk == len(token_list):
            tk = 0

        print("iteration ", i, "/", len(solar_df)-1)
        print("tk ", tk, token_list[tk])

        coordinate = [row["Latitude"], row["Longitude"]]
        capacity = row["Capacity (MW)"]

        temp_data, temp_metadata = pv_request(
            coordinates=coordinate,
            year=year_solar,
            token=token_list[tk],
            capacity=capacity,
            system_loss=system_loss,
            tracking=tracking,
            tilt=tilt,
            azim=azim
        )

        print(temp_data)
        print(temp_metadata)
        
        raise Exception

        tk += 1