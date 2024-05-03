import os
import requests
from osgeo import gdal
import json

def data_obtain():
    url = 'https://api.openinframap.org/infrastructure'
    json_path = "./data/openinfra.json"
    # Send a GET request to retrieve the TileJSON data
    with open(json_path, 'r') as file:
        request_json = json.load(file)
    
    response = requests.post(url, json=request_json)
    print(response)



def pbf_to_shapefile(input_pbf, output_shapefile):
    # Convert PBF to Shapefile
    gdal.VectorTranslate(
        output_shapefile,  # Output shapefile path
        input_pbf,         # Input PBF file path
        format='ESRI Shapefile'  # Output format
    )



if __name__ == "__main__":
    
    pbf_to_shapefile('./tiles/2_0_0.pbf', './output.shp')
    
    #data_obtain()