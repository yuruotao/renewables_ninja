# import the necessary dependencies
import pandas as pd
import numpy as np
from pathlib import Path
import osmnx as ox
import geopandas as gpd
import matplotlib.pyplot as plt

# Import the infrastructure data
def infra_data_import():
    import pandas as pd
    import geopandas as gpd
    
    base = "./data/plot_data/infra_data/"
    atomic_data = base + "atomic.csv"
    solar_data = base + "solar.xlsx"
    thermal_data = base + "thermal.csv"
    wind_data = base + "wind.xlsx"
    gas_data = base + "gas.csv"
    water_data = base + "water.xlsx"
    
    # Import the shapefile of interested place
    gdf_provincial = gpd.read_file("./data/shape_data/guangxi/guangxi.shp")
    
    # Import the data
    atomic = pd.read_csv(atomic_data, index_col=None)
    atomic.rename(columns = {'capacity_mw':'MW'}, inplace = True)
    atomic = atomic[atomic["country"] == "CHN"]
    
    gas_0 = atomic[atomic["primary_fuel"] == "Gas"]
    thermal_0 = atomic[atomic["primary_fuel"] == "Coal"]
    water_0 = atomic[atomic["primary_fuel"] == "Hydro"]
    solar_0 = atomic[atomic["primary_fuel"] == "Solar"]
    wind_0 = atomic[atomic["primary_fuel"] == "Wind"]
    
    atomic = atomic[atomic["primary_fuel"] == "Nuclear"]
    atomic = atomic.reset_index()
    atomic = atomic[["MW","longitude", "latitude"]]
    atomic = df_to_gdf(atomic, "longitude", "latitude")
    atomic = gpd.sjoin(atomic, gdf_provincial, how='inner', op='within')

    gas = pd.read_csv(gas_data, index_col=None)
    gas.rename(columns = {'capacity_mw':'MW'}, inplace = True)
    gas = gas[gas["province.1"] == "Guangxi"]
    gas = gas[["MW","longitude", "latitude"]]
    gas = gas.append(gas_0, ignore_index = True)
    gas = gas.reset_index()
    gas = df_to_gdf(gas, "longitude", "latitude")
    gas = gpd.sjoin(gas, gdf_provincial, how='inner', op='within')
    
    thermal = pd.read_csv(thermal_data, index_col=None, encoding = "ISO-8859-1", on_bad_lines='skip')
    thermal.rename(columns = {'Capacity_MW':'MW', "Longitude":"longitude", "Latitude":"latitude"}, inplace = True)
    thermal = thermal[thermal["province"] == "Guangxi"]
    thermal = thermal[["MW","longitude", "latitude"]]
    thermal = thermal.append(thermal_0, ignore_index = True)
    thermal = thermal.reset_index()
    thermal = df_to_gdf(thermal, "longitude", "latitude")
    thermal = gpd.sjoin(thermal, gdf_provincial, how='inner', op='within')
    
    water = pd.read_excel(water_data, index_col=None)
    water.rename(columns = {'Install_Nom':'MW', "Lon_P_X":"longitude", "Lat_P_Y":"latitude"}, inplace = True)
    water = water[water["Province"] == "Guangxi"]
    water = water[["MW","longitude", "latitude"]]
    water = water.append(water_0, ignore_index = True)
    water = water.reset_index()
    water = df_to_gdf(water, "longitude", "latitude")
    water = gpd.sjoin(water, gdf_provincial, how='inner', op='within')
    
    #########################################################
    # No coordinates
    solar = pd.read_excel(solar_data, index_col=None)
    solar['MW'] = solar['MW'].replace('', np.nan)
    solar = solar.dropna(subset=['MW'])
    solar['编号'] = solar['编号'].replace('编号', np.nan)
    solar = solar.dropna(subset=['编号'])
    solar = solar[["MW","longitude", "latitude"]]
    solar = solar.append(solar_0, ignore_index = True)
    solar = solar.reset_index()
    solar = df_to_gdf(solar, "longitude", "latitude")
    solar = gpd.sjoin(solar, gdf_provincial, how='inner', op='within')
    
    wind = pd.read_excel(wind_data, index_col=None)
    wind['MW'] = wind['MW'].replace('', np.nan)
    wind = wind.dropna(subset=['MW'])
    wind['编号'] = wind['编号'].replace('编号', np.nan)
    wind = wind.dropna(subset=['编号'])
    wind = wind[["MW","longitude", "latitude"]]
    wind = wind.append(wind_0, ignore_index = True)
    wind = wind.reset_index()
    wind = df_to_gdf(wind, "longitude", "latitude")
    wind = gpd.sjoin(wind, gdf_provincial, how='inner', op='within')
    
    return atomic, solar, thermal, wind, gas, water

def province_grid_mapping(province, graph, path, plot_state):
    """

    Args:
        province (string): the province to be plotted
        path (_type_): _description_
        plot_state (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Add the provincial border line
    # https://data.humdata.org/dataset/cod-ab-chn
    gdf_provincial = gpd.read_file("./data/shape_data/"+ province + "/" + province + ".shp")

    # Plot the figure
    if plot_state == 1:
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
        # Add data
        atomic, solar, thermal, wind, gas, water = infra_data_import()
        water.plot(ax=ax, color="#0077b6", markersize=water["MW"], alpha = 0.5, label="Hydro", legend=True)
        thermal.plot(ax=ax, color="#001427", markersize=thermal["MW"], alpha = 0.5, label="Thermal")
        solar.plot(ax=ax, color="#fca311", markersize=solar["MW"], alpha = 0.5, label="Solar")
        gas.plot(ax=ax, color="#9d4edd", markersize=gas["MW"], alpha = 0.5, label="Gas")
        atomic.plot(ax=ax, color="#d62828", markersize=atomic["MW"], alpha = 0.5, label="Nuclear")
        wind.plot(ax=ax, color="#70e000", markersize=wind["MW"], alpha = 0.5, label="Wind")
        
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
        plt.savefig(path + province +"/_solar.png", dpi=900)
        plt.show()

    return graph

if __name__ == "__main__":
    

    