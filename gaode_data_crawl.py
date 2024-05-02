# coding: utf-8
import requests
import numpy as np
import time


# Get the lat and lon of the locations for tesla_cn with BaiduMap
def gaode_data_obtain():
    api_key = "e3103237574917e1d68ae02d49af7cbf"
    url = "https://restapi.amap.com/v3/charging/queryStationInfo"
    params = {
    "key": api_key,
    "output": "json",  # Specify output format (JSON or XML)
    # Add any other parameters required by the service
    }

    response = requests.get(url, params=params)
    print(response)
    data = response.json()
    print(data)
    time.sleep(100)

    


if __name__ == "__main__":
    gaode_data_obtain()



