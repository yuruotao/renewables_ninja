# coding: utf-8
import os
import requests
import json
import geopandas as gpd
import time
import osmium
from osgeo import ogr

def osm_to_shapefile(input_osm_file, output_shapefile):
    driver = ogr.GetDriverByName("OSM")
    data_source = driver.Open(input_osm_file, update=False)

    if data_source is None:
        print("Failed to open input OSM file.")
        return

    layer = data_source.GetLayer()
    
    # Create a shapefile
    shape_driver = ogr.GetDriverByName("ESRI Shapefile")
    shape_data_source = shape_driver.CreateDataSource(output_shapefile)

    # Create a new layer in the shapefile
    shape_layer = shape_data_source.CreateLayer("layer", geom_type=ogr.wkbMultiLineString)

    # Copy fields from OSM layer to shapefile layer
    layer_defn = layer.GetLayerDefn()
    for i in range(layer_defn.GetFieldCount()):
        field_defn = layer_defn.GetFieldDefn(i)
        shape_layer.CreateField(field_defn)

    # Copy features from OSM layer to shapefile layer
    for feature in layer:
        shape_layer.CreateFeature(feature)

    # Close data sources
    data_source = None
    shape_data_source = None



if __name__ == "__main__":
    #./osmfilter china.osm --keep="highway=pipeline power=tower =substation =generator =plant = transformer =compensator =switch telecoms=line =mast =data_center man_made=mast =petroleum_well =petroleum_pipeline =petroleum_site =water_pipeline" >filtered.osm
    input_osm_file = "./data/filtered.osm"
    output_shapefile = "./output.shp"

    osm_to_shapefile(input_osm_file, output_shapefile)