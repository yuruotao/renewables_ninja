import os
import requests
from osgeo import gdal
import json
import geopandas as gpd
import time
import osmium
from shapely.geometry import LineString, Point

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

class OSMHandler(osmium.SimpleHandler):
    def __init__(self):
        super(OSMHandler, self).__init__()
        self.geometries = []

    def way(self, w):
        coords = [(n.lon, n.lat) for n in w.nodes]
        geometry = LineString(coords)
        self.geometries.append(geometry)
            
    def node(self, n):
        geometry = Point(n.lon, n.lat)
        self.geometries.append(geometry)

if __name__ == "__main__":
    """
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
    """

    input_file = "./data/china.osm"
    output_file = "./output.osm"
    filter_tags = ["highway=pipeline", "power=line", "power=tower", "power=substation", 
                "power=generator", "power=plant", "power=transformer", "power=compensator", 
                "power=switch", "telecoms=line", "telecoms=mast", "telecoms=data_center", 
                "man_made=mast", "man_made=petroleum_well", "man_made=petroleum_pipeline", 
                "man_made=petroleum_site", "man_made=water_pipeline"]
    
    #./osmfilter china.osm --keep="highway=pipeline power=tower =substation =generator =plant = transformer =compensator =switch telecoms=line =mast =data_center man_made=mast =petroleum_well =petroleum_pipeline =petroleum_site =water_pipeline" >filtered.osm



    input_osm_file = "./data/filtered.osm"
    output_shapefile = "./output.shp"

    handler = OSMHandler()
    handler.apply_file(input_osm_file)

    # Convert lines to GeoDataFrame
    gdf_lines = gpd.GeoDataFrame(geometry=handler.lines)

    # Convert points to GeoDataFrame
    gdf_points = gpd.GeoDataFrame(geometry=handler.points)

    # Save GeoDataFrames to shapefiles
    gdf_lines.to_file(output_shapefile.replace('.shp', '_lines.shp'))
    gdf_points.to_file(output_shapefile.replace('.shp', '_points.shp'))
