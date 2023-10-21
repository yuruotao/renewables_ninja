import requests
import pandas as pd
import datetime as dt
from pathlib import Path
import os
import json
from dataclasses import dataclass
from io import StringIO
from typing import Dict, Union

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

API_BASE_URL = "https://www.renewables.ninja/api"
PV_URL = f"{API_BASE_URL}/data/pv"
WIND_URL = f"{API_BASE_URL}/data/wind"
DATE_FORMAT = "%Y-%m-%d"
TOKEN_FILENAME = 'ninja_token.json'

from dataclasses import dataclass

@dataclass(frozen=True)
class Client:
    token: str
    pv_url: str = PV_URL
    wind_url: str = WIND_URL

    @classmethod
    def from_df(cls, path=None, token_filename: str = None):
        if path is None:
            path = "./data/model_input/"
        if token_filename is None:
            token_filename = "ninja_accounts.xlsx"
        file_path = path + token_filename
        
        return cls(_load_token(file_path))


def get_headers(client: Client) -> Dict[str, str]:
    return {'Authorization': 'Token ' + client.token}

def date_to_str(date: Union[dt.date,dt.datetime], date_format:str=DATE_FORMAT) -> str:
    return date.strftime(date_format)

def _get_path_to_module():
    '''Get path to this module.'''
    return Path(os.path.realpath(__file__)).parent

def _load_token(filename):
    '''Load token.'''
    with open(filename, 'r') as f:
        return json.load(f)['token']

def query_pv(
    client: Client,
    date_from: Union[dt.date, dt.datetime], 
    date_to: Union[dt.date, dt.datetime], 
    lat: float,
    lon: float, 
    tilt: float, 
    azim: float, 
    capacity: float, 
    system_loss: float = .1, 
    tracking: bool = False, 
    dataset: str = 'merra2', 
    interpolate: bool = False, 
    local_time: bool = False, 
    raw: bool = False,
    ) -> pd.DataFrame:

    headers = get_headers(client)

    params = {
        'date_from': date_to_str(date_from),
        'date_to': date_to_str(date_to),
        'lat': lat,
        'lon': lon,
        'tilt': tilt,
        'azim': azim,
        'capacity': capacity,
        'system_loss': system_loss,
        'tracking': tracking,
        'dataset': dataset,
        'interpolate': interpolate,
        'local_time': local_time,
        'raw': raw,
        'format': 'csv',
        'header': False,
    }

    r = requests.get(client.pv_url, params=params, headers=headers)

    if not r.ok:
        logger.error("Query failed with status {}: {}".format(r.status_code, r.text))
        r.raise_for_status()
    return pd.read_csv(StringIO(r.text), index_col=0)

def query_wind(
    client: Client,
    date_from: Union[dt.date, dt.datetime], 
    date_to: Union[dt.date, dt.datetime], 
    lat: float,
    lon: float, 
    height: float, 
    capacity: float = 1., 
    turbine='Vestas V80 2000', 
    interpolate: bool = False, 
    local_time: bool = False, 
    raw: bool = False,
    ) -> pd.DataFrame:

    headers = get_headers(client)

    params = {
        'date_from': date_to_str(date_from),
        'date_to': date_to_str(date_to),
        'lat': lat,
        'lon': lon,
        'height': height,
        'capacity': capacity,
        'turbine': turbine,
        'raw': raw,
        'interpolate': interpolate,
        'local_time': local_time,
        'format': 'csv',
        'header': False,
    }

    r = requests.get(client.wind_url, params=params, headers=headers)

    if not r.ok:
        logger.error("Query failed with status {}: {}".format(r.status_code, r.text))
        r.raise_for_status()
    return pd.read_csv(StringIO(r.text), index_col=0)