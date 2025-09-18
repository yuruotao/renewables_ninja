# import the necessary dependencies
import pandas as pd
import numpy as np
from pathlib import Path
import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt
import momepy
import os

from deprecated import data_import
from utils import scraper_utils

current_path = str(Path())
input_data_path = current_path + "/data/model_input"
lat_lon_path = input_data_path + "/china_mass_center_2019.xlsx"
solar_path = input_data_path + "/Global-Solar-Power-Tracker.xlsx"
accounts_path = input_data_path + "/ninja_accounts.xlsx"
wind_path = input_data_path + "/.xlsx"

province_name_list = [
    "Anhui",
    "Beijing",
    "Chongqing",
    "Fujian",
    "Gansu",
    "Guangdong",
    "Guangxi",
    "Guizhou",
    "Hainan",
    "Hebei",
    "Heilongjiang",
    "Henan",
    "Hubei",
    "Hunan",
    "Inner Mongolia",
    "Jiangsu",
    "Jiangxi",
    "Jilin",
    "Liaoning",
    "Ningxia",
    "Qinghai",
    #"Shannxi",
    "Shandong",
    "Shanghai",
    "Shanxi",
    "Sichuan",
    "Tianjin",
    "Tibet",
    "Xinjiang",
    "Yunnan",
    "Zhejiang",
]

def df_to_gdf(df, lon_name, lat_name):
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import Point
    
    # Designate the coordinate system
    crs = {'init':'EPSG:4326'}
    # Construct the geometry for geodataframe
    geometry = [Point(xy) for xy in zip(df[lon_name], df[lat_name])]
    gdf = gpd.GeoDataFrame(df, 
                          crs = crs, 
                          geometry = geometry)
    
    return gdf

def province_grid_mapping_solar(province, path, plot_state):
    """

    Args:
        province (string): the province to be plotted
        path (_type_): _description_
        plot_state (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    if not os.path.exists(path):
        os.makedirs(path)
    
    # Add the provincial border line
    # https://data.humdata.org/dataset/cod-ab-chn
    gdf_provincial = gpd.read_file("./data/shape_data/"+ province + "/" + province + ".shp")
    
    # Add data
    solar_df = data_import.solar_power_import(solar_path)
    solar_df = solar_df[solar_df["State/Province"]==province]
    solar = df_to_gdf(solar_df, "Longitude", "Latitude")
    solar = gpd.sjoin(solar, gdf_provincial, how='inner', op='within')

    # Plot the figure
    if plot_state == 1:
        graph = momepy.gdf_to_nx(solar, approach='primal')
        fig, ax = ox.plot_graph(graph,
                                bgcolor="#FFFFFF",
                                node_color="#457b9d",
                                node_size=0,
                                edge_color="#000000",
                                save=False,
                                close=False,
                                show=False)

        # Add the place shape to this matplotlib axis
        gdf_provincial.plot(ax=ax, ec="#d9d9d9", lw=1, facecolor="none")
        
        #####################################################################
        solar.plot(ax=ax, color="#fca311", markersize=5*solar["Capacity (MW)"], alpha = 0.5, label="Solar")

        
        # Set the label
        #####################################################################
        
        #size_values = [1, 10]  # Choose the specific size values you want to include in the legend
        #legend_labels = [str(size) for size in size_values]

        # Create custom legend handles with the chosen size values
        #handles = [plt.Line2D([], [], marker='o', linestyle='None', markersize=size, label=label, alpha = 0.5) for size, label in zip(size_values, legend_labels)]
        #ax.legend(labels=legend_labels, handles=handles, bbox_to_anchor=(1.05, 1))

        #####################################################################

        # Optionally set up the axes extents
        margin = 0.02
        west, south, east, north = gdf_provincial.unary_union.bounds
        margin_ns = (north - south) * margin
        margin_ew = (east - west) * margin
        ax.set_ylim((south - margin_ns, north + margin_ns))
        ax.set_xlim((west - margin_ew, east + margin_ew))
        
        # Save and show figure
        plt.savefig(path + province +"_solar.png", dpi=900)
        #plt.show()

    return None



if __name__ == "__main__":
    

    for province in province_name_list:
        province_grid_mapping_solar(province, "./results/figure/solar/", 1)
    