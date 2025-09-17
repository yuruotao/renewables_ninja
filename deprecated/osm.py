from osgeo import ogr
from osgeo import osr

osm_file = "./data/osm_data/china-latest.osm"
shp_file = "./results/china_osm.shp"

osm_driver = ogr.GetDriverByName('OSM')

osm_ds = ogr.Open(osm_file)
if osm_ds is None:
    print("Failed to open OSM file.")
    exit(1)

shp_driver = ogr.GetDriverByName('ESRI Shapefile')
shp_ds = shp_driver.CreateDataSource(shp_file)
if shp_ds is None:
    print("Failed to create SHP file.")
    exit(1)

for osm_layer in osm_ds:
    shp_layer = shp_ds.CreateLayer(osm_layer.GetName(), geom_type=ogr.wkbUnknown)

    for osm_feature in osm_layer:
        shp_feature = ogr.Feature(shp_layer.GetLayerDefn())

        # Copy attributes
        for field in osm_feature.keys():
            shp_feature.SetField(field, osm_feature.GetField(field))

        # Copy geometry
        osm_geom = osm_feature.GetGeometryRef()
        if osm_geom is not None:
            shp_feature.SetGeometry(osm_geom.Clone())

        shp_layer.CreateFeature(shp_feature)
