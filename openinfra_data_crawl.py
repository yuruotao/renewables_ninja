import os
import requests
from osgeo import gdal
import json
import geopandas as gpd
import time



def pbf_to_shapefile(input_pbf, output_shapefile):
    # Convert PBF to Shapefile
    #epsg_code = 'EPSG:3857'
    #options = gdal.VectorTranslateOptions(options=f"-s_srs {epsg_code}")

    gdal.VectorTranslate(
        output_shapefile,  # Output shapefile path
        input_pbf,         # Input PBF file path
        format='ESRI Shapefile',  # Output format
        #options=options
    )



if __name__ == "__main__":
    
    # Fetch TileJSON data
    tilejson_url = 'https://openinframap.org/map.json'
    response = requests.get(tilejson_url)
    tilejson_data = response.json()
    vector_layer_base_url = tilejson_data['tiles'][0]

    # Loop through each vector layer in the TileJSON data
    for layer in tilejson_data['vector_layers']:
        print(layer)
        id = layer.get("id")
        # Construct the URL for the vector layer
        vector_layer_url = vector_layer_base_url.format(z=17, x=0, y=0)  # Assuming we fetch from zoom level 0
        
        # Fetch the vector layer data
        response = requests.get(vector_layer_url)
        print(response)

        # Convert the vector layer data to GeoDataFrame
        result_pbf = response.content

        temp_save_path = "./results/openinfra/pbf/"
        if not os.path.exists(temp_save_path):
            os.mkdir(temp_save_path)
        
        shp_temp_save_path = "./results/openinfra/shp/" + id + "/"
        if not os.path.exists(shp_temp_save_path):
            os.mkdir(shp_temp_save_path)
        
        with open(temp_save_path + id + ".pbf", 'wb') as f:
            f.write(result_pbf)
        
        pbf_to_shapefile("./results/openinfra/pbf/" + id + ".pbf" , 
                         shp_temp_save_path + id + ".shp")
        
        temp_gpd = gpd.read_file(shp_temp_save_path + id + ".shp")
        temp_gpd.set_crs('EPSG:3857', allow_override=True, inplace=True)
        temp_gpd.to_crs('EPSG:4326', inplace=True)
        temp_gpd.to_file(shp_temp_save_path + id + ".shp")
        
