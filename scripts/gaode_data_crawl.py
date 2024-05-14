# coding: utf-8
import requests
import numpy as np
import time
import json
import math
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from DrissionPage import ChromiumPage
from matplotlib.patches import Patch
import seaborn as sns

sns.set_style({'font.family':'serif', 'font.serif':'Times New Roman'})
sns.set_theme(style="white")

# Get the charging stations in amap
def gaode_charging_data_obtain_api(city_adcode):
    """Obtain the charging data of gaode map with api

    Args:
        city_adcode (int): the adminstration code of city

    Returns:
        Ture
    """
    json_save_path = "./results/gaode/json/"
    api_key = "e3103237574917e1d68ae02d49af7cbf"
    
    # https://lbs.amap.com/api/webservice/guide/api/search
    # https://lbs.amap.com/api/webservice/download
    # 011100	汽车服务	充电站	充电站
    # 011102	汽车服务	充电站	充换电站
    # 011103	汽车服务	充电站	专用充电站
    # 073000	生活服务	电动自动车充电站	电动自行车充电站
    # 073001	生活服务	电动自动车充电站	电动自行车换电站
    # 073002	生活服务	电动自动车充电站	电动自行车专用充电站
    base_website_api = "https://restapi.amap.com/v3/place/text?key={api_key}&types=011100|011102|011103&citylimit=True&city={city}&page={page_num}"
    test_url = base_website_api.format(api_key=api_key, city=city_adcode, page_num=1)

    test_json = requests.get(test_url, timeout=(10,10)).json()
    count = int(test_json["count"])
    print(count)
    merged_json = test_json["pois"]
    
    if count <= 20:
        pass
    else: # More than one page
        total_page_num = math.ceil(count/20)
        for page in range(2, total_page_num + 1):
            print("Page", page)
            temp_url = base_website_api.format(api_key=api_key, city=city_adcode, page_num=page)
            temp_json = requests.get(temp_url).json()
            temp_pois = temp_json["pois"]
            merged_json = merged_json + temp_pois
            
    merged_json_str = json.dumps(merged_json, indent=2)
    with open(json_save_path + str(city_adcode) + ".json", "w") as json_file:
        # Write JSON string to file
        json_file.write(merged_json_str)
    
    return True

# Gather the minimal adminstration code
def adminstration_code_data(json_path):
    """Make a list from json including the adminstration code

    Args:
        json_path (string): path to the json file

    Returns:
        list: a list containing strings representing adminstration code
    """
    with open(json_path, "r", encoding="utf") as f:
        city_info = json.load(f)
    adcode_list = []
    zhixiashi = ["11","12","31","50"]
    for i in range(len(city_info)):
        if (city_info[i]["adcode"][-4:] == "0000"):
            continue
        if ((city_info[i]["adcode"][-2:] == "00" ) or (city_info[i]["adcode"][-2:] == "01" and city_info[i]["adcode"][:2] not in zhixiashi)):
            continue
        adcode_list.append(city_info[i]["adcode"])
    return adcode_list

# Get the lat and lon of the locations for tesla_cn with BaiduMap
def gaode_haha_data_obtain_api(city_adcode):
    """Obtain the interesting data of gaode map with api

    Args:
        city_adcode (int): the adminstration code of city

    Returns:
        Ture
    """
    #json_save_path = "./results/gaode_haha/json/"
    json_save_path = "./results/gaode_entertain/json/"
    api_key = "e3103237574917e1d68ae02d49af7cbf"
    
    # haha
    # https://lbs.amap.com/api/webservice/guide/api/search
    # https://lbs.amap.com/api/webservice/download
    # 050300	餐饮服务	快餐厅	快餐厅
    # 050301	餐饮服务	快餐厅	肯德基
    # 050302	餐饮服务	快餐厅	麦当劳
    # 050303	餐饮服务	快餐厅	必胜客
    # 050304	餐饮服务	快餐厅	永和豆浆
    # 050305	餐饮服务	快餐厅	茶餐厅
    # 050306	餐饮服务	快餐厅	大家乐
    # 050307	餐饮服务	快餐厅	大快活
    # 050308	餐饮服务	快餐厅	美心
    # 050309	餐饮服务	快餐厅	吉野家
    # 050310	餐饮服务	快餐厅	仙跡岩
    # 050311	餐饮服务	快餐厅	呷哺呷哺
    # 050400	餐饮服务	休闲餐饮场所	休闲餐饮场所
    
    # entertainment
    # 080300	体育休闲服务	娱乐场所	娱乐场所
    # 080301	体育休闲服务	娱乐场所	夜总会
    # 080302	体育休闲服务	娱乐场所	KTV
    # 080303	体育休闲服务	娱乐场所	迪厅
    # 080304	体育休闲服务	娱乐场所	酒吧
    # 080305	体育休闲服务	娱乐场所	游戏厅
    # 080306	体育休闲服务	娱乐场所	棋牌室
    # 080307	体育休闲服务	娱乐场所	博彩中心
    # 080308	体育休闲服务	娱乐场所	网吧

    #base_website_api = "https://restapi.amap.com/v3/place/text?key={api_key}&types=050300|050301|050302|050303|050304|050305|050306|050307|050308|050309|050310|050311|050400&citylimit=True&city={city}&page={page_num}"
    base_website_api = "https://restapi.amap.com/v3/place/text?key={api_key}&types=080301|080302|080303|080304&citylimit=True&city={city}&page={page_num}"
    test_url = base_website_api.format(api_key=api_key, city=city_adcode, page_num=1)

    test_json = requests.get(test_url).json()
    count = int(test_json["count"])
    print(count)
    merged_json = test_json["pois"]
    
    if count <= 20:
        pass
    else: # More than one page
        total_page_num = math.ceil(count/20)
        for page in range(2, total_page_num + 1):
            print("Page", page)
            temp_url = base_website_api.format(api_key=api_key, city=city_adcode, page_num=page)
            temp_json = requests.get(temp_url).json()
            temp_pois = temp_json["pois"]
            merged_json = merged_json + temp_pois
            
    merged_json_str = json.dumps(merged_json, indent=2)
    with open(json_save_path + str(city_adcode) + ".json", "w") as json_file:
        # Write JSON string to file
        json_file.write(merged_json_str)
    
    return True

def gaode_luckin_data_obtain_api(city_adcode):
    """Obtain the interesting data of gaode map with api

    Args:
        city_adcode (int): the adminstration code of city

    Returns:
        Ture
    """
    #json_save_path = "./results/gaode_haha/json/"
    json_save_path = "./results/gaode_luckin_coffee/json/"
    api_key = "e3103237574917e1d68ae02d49af7cbf"
    
    base_website_api = "https://restapi.amap.com/v3/place/text?key={api_key}&keywords={keyword}&citylimit=True&city={city}&page={page_num}"
    test_url = base_website_api.format(api_key=api_key, city=city_adcode, page_num=1, keyword="瑞幸咖啡")

    test_json = requests.get(test_url).json()
    count = int(test_json["count"])
    print(count)
    merged_json = test_json["pois"]
    
    if count <= 20:
        pass
    else: # More than one page
        total_page_num = math.ceil(count/20)
        for page in range(2, total_page_num + 1):
            print("Page", page)
            temp_url = base_website_api.format(api_key=api_key, city=city_adcode, page_num=page, keyword="瑞幸咖啡")
            temp_json = requests.get(temp_url).json()
            temp_pois = temp_json["pois"]
            merged_json = merged_json + temp_pois
            
    merged_json_str = json.dumps(merged_json, indent=2)
    with open(json_save_path + str(city_adcode) + ".json", "w") as json_file:
        # Write JSON string to file
        json_file.write(merged_json_str)
    
    return True

def gaode_cotti_data_obtain_api(city_adcode):
    """Obtain the interesting data of gaode map with api

    Args:
        city_adcode (int): the adminstration code of city

    Returns:
        Ture
    """
    #json_save_path = "./results/gaode_haha/json/"
    json_save_path = "./results/gaode_cotti_coffee/json/"
    api_key = "e3103237574917e1d68ae02d49af7cbf"
    
    base_website_api = "https://restapi.amap.com/v3/place/text?key={api_key}&keywords={keyword}&citylimit=True&city={city}&page={page_num}"
    test_url = base_website_api.format(api_key=api_key, city=city_adcode, page_num=1, keyword="库迪咖啡")

    test_json = requests.get(test_url).json()
    count = int(test_json["count"])
    print(count)
    merged_json = test_json["pois"]
    
    if count <= 20:
        pass
    else: # More than one page
        total_page_num = math.ceil(count/20)
        for page in range(2, total_page_num + 1):
            print("Page", page)
            temp_url = base_website_api.format(api_key=api_key, city=city_adcode, page_num=page, keyword="库迪咖啡")
            temp_json = requests.get(temp_url).json()
            temp_pois = temp_json["pois"]
            merged_json = merged_json + temp_pois
            
    merged_json_str = json.dumps(merged_json, indent=2)
    with open(json_save_path + str(city_adcode) + ".json", "w") as json_file:
        # Write JSON string to file
        json_file.write(merged_json_str)
    
    return True

# 
def obtain_detail_by_id(input_df_path):
    
    charging_df = pd.read_excel(input_df_path)
    try:
        base_url = "https://amap.com/place/"
        page = ChromiumPage()
        page.get(base_url)  # 访问网址，这行产生的数据包不监听
        page.listen.start('amap.com/detail/get/detail')  # 开始监听，指定获取包含该文本的数据包
        
        for index, row in charging_df.iterrows():
            print(index)
            temp_id = row["id"]
            page.get(base_url + temp_id)            
            res = page.listen.wait()
            detail_json = res.response.body            
            detail_json = detail_json['data']
            print(detail_json)
            time.sleep(100)
            #db.update(table='gaode_pois',                      
            #        data={'detail_json_data': json.dumps(detail_json)},                      
            #        condition=f" poi_id = '{poi_id}'")
    except Exception as e:
        print(e)
    
def df_to_gdf(df, lon_name, lat_name):
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import Point
    
    # Construct the geometry for geodataframe
    geometry = [Point(xy) for xy in zip(df[lon_name], df[lat_name])]
    gdf = gpd.GeoDataFrame(df, 
                          crs = 'EPSG:4326', 
                          geometry = geometry)
    return gdf

def visualization(input_df_path, province, type):
    charging_df = pd.read_excel(input_df_path)
    charging_df = charging_df.dropna(subset=['lat'])
    charging_df = charging_df.astype({"lat":float, "lon":float})
    gdf_province = gpd.read_file("./data/shape_data/"+ province + "/" + province + ".shp")
    gdf_china = gpd.read_file("./data/shape_data/China/chn_admbnda_adm1_ocha_2020.shp")
    charging_gdf = df_to_gdf(charging_df, "lon", "lat")
    
    # Plot for china
    plt.figure(figsize=(20, 15))
    gdf_china.boundary.plot(linewidth=0.5, color="#adb5bd", zorder=1)
    bounds = gdf_china.total_bounds
    ax = plt.gca()
    
    # Set the aspect of the plot to be equal
    ax.set_aspect('equal')
    extend = 0
    ax.set_xlim(bounds[0]-extend, bounds[2]+extend)
    ax.set_ylim(bounds[1]-extend, bounds[3]+extend)
    ax.axis('off')

    num_ratio = 0.005

    for index, row in charging_gdf.iterrows():
        if row["typecode"] == "050301": #KFC
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#c81d25', linewidths=0, edgecolor=None, alpha=1)
        elif row["typecode"] == "050302": #M
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#fca311', linewidths=0, edgecolor=None, alpha=1)
        elif "汉堡王" in row["name"]: #Burgerking
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#540b0e', linewidths=0, edgecolor=None, alpha=1)
        else:
            pass
    
    # Define custom legend handles and labels
    legend_handles = [
        Patch(color='#c81d25', label='KFC'),
        Patch(color='#fca311', label='McDonalds'),
        Patch(color='#540b0e', label='Burger King')
    ]

    # Add legend to the plot
    legend = plt.legend(handles=legend_handles, loc='upper left', frameon=False, 
                        bbox_to_anchor=(0, 1.02, 1, 0.2), mode="expand", borderaxespad=0, ncol=3)
    
    for text in legend.get_texts():
        text.set_fontfamily('Times New Roman')

    #plt.tight_layout()
    plt.savefig("./results/" + type + "_cn.png", dpi=900)
    plt.close()
    
    # Plot for province
    charging_province = gpd.sjoin(charging_gdf, gdf_province, how='inner', op='within')
    plt.figure(figsize=(20, 15))
    gdf_province.boundary.plot(linewidth=0.5, color="#adb5bd", zorder=1)
    bounds = gdf_province.total_bounds
    ax = plt.gca()
    
    # Set the aspect of the plot to be equal
    ax.set_aspect('equal')
    extend = 0
    ax.set_xlim(bounds[0]-extend, bounds[2]+extend)
    ax.set_ylim(bounds[1]-extend, bounds[3]+extend)
    ax.axis('off')
    
    num_ratio = 0.02
    
    for index, row in charging_province.iterrows():
        if row["typecode"] == "050301": #KFC
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#c81d25', edgecolor=None, alpha=1)
        elif row["typecode"] == "050302": #M
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#fca311', edgecolor=None, alpha=1)
        elif "汉堡王" in row["name"]: #Burgerking
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#540b0e', edgecolor=None, alpha=1)
        else:
            pass
    
    # Define custom legend handles and labels
    legend_handles = [
        Patch(color='#c81d25', label='KFC'),
        Patch(color='#fca311', label='McDonalds'),
        Patch(color='#540b0e', label='Burger King')
    ]

    # Add legend to the plot
    legend = plt.legend(handles=legend_handles, loc='upper left', frameon=False, 
                        bbox_to_anchor=(0, 1.02, 1, 0.2), mode="expand", borderaxespad=0, ncol=3)
    
    for text in legend.get_texts():
        text.set_fontfamily('Times New Roman')
    
    #plt.tight_layout()
    plt.savefig("./results/" + type + "_province.png", dpi=900)
    plt.close()

def entertain_visualization(input_df_path, province, type):
    charging_df = pd.read_excel(input_df_path)
    charging_df = charging_df.dropna(subset=['lat'])
    charging_df = charging_df.astype({"lat":float, "lon":float})
    gdf_province = gpd.read_file("./data/shape_data/"+ province + "/" + province + ".shp")
    gdf_china = gpd.read_file("./data/shape_data/China/chn_admbnda_adm1_ocha_2020.shp")
    charging_gdf = df_to_gdf(charging_df, "lon", "lat")
    
    # Plot for china
    plt.figure(figsize=(20, 15))
    gdf_china.boundary.plot(linewidth=0.5, color="#adb5bd", zorder=1)
    bounds = gdf_china.total_bounds
    ax = plt.gca()
    
    # Set the aspect of the plot to be equal
    ax.set_aspect('equal')
    extend = 0
    ax.set_xlim(bounds[0]-extend, bounds[2]+extend)
    ax.set_ylim(bounds[1]-extend, bounds[3]+extend)
    ax.axis('off')

    num_ratio = 0.01

    for index, row in charging_gdf.iterrows():
        if row["typecode"] == "080301": #夜总会
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#001427', linewidths=0, edgecolor=None, alpha=1)
        elif row["typecode"] == "080302": #KTV
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#708d81', linewidths=0, edgecolor=None, alpha=1)
        elif row["typecode"] == "080303": #迪厅
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#f4d58d', linewidths=0, edgecolor=None, alpha=1)
        elif row["typecode"] == "080304": #酒吧
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#bf0603', linewidths=0, edgecolor=None, alpha=1)
        else:
            pass
    
    # Define custom legend handles and labels
    legend_handles = [
        Patch(color='#001427', label='Night Club'),
        Patch(color='#708d81', label='KTV'),
        Patch(color='#f4d58d', label='Disco'),
        Patch(color='#bf0603', label='Bar')
    ]
    
    # Add legend to the plot
    legend = plt.legend(handles=legend_handles, loc='upper left', frameon=False, 
                        bbox_to_anchor=(0, 1.02, 1, 0.2), mode="expand", borderaxespad=0, ncol=4)
    
    for text in legend.get_texts():
        text.set_fontfamily('Times New Roman')

    #plt.tight_layout()
    plt.savefig("./results/" + type + "_cn.png", dpi=900)
    plt.close()
    
    # Plot for province
    charging_province = gpd.sjoin(charging_gdf, gdf_province, how='inner', op='within')
    plt.figure(figsize=(20, 15))
    gdf_province.boundary.plot(linewidth=0.5, color="#adb5bd", zorder=1)
    bounds = gdf_province.total_bounds
    ax = plt.gca()
    
    # Set the aspect of the plot to be equal
    ax.set_aspect('equal')
    extend = 0
    ax.set_xlim(bounds[0]-extend, bounds[2]+extend)
    ax.set_ylim(bounds[1]-extend, bounds[3]+extend)
    ax.axis('off')
    
    num_ratio = 0.02
    
    for index, row in charging_province.iterrows():
        if row["typecode"] == "080301": #夜总会
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#001427', linewidths=0, edgecolor=None, alpha=1)
        elif row["typecode"] == "080302": #KTV
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#708d81', linewidths=0, edgecolor=None, alpha=1)
        elif row["typecode"] == "080303": #迪厅
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#f4d58d', linewidths=0, edgecolor=None, alpha=1)
        elif row["typecode"] == "080304": #酒吧
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#bf0603', linewidths=0, edgecolor=None, alpha=1)
        else:
            pass
    
    # Define custom legend handles and labels
    legend_handles = [
        Patch(color='#001427', label='Night Club'),
        Patch(color='#708d81', label='KTV'),
        Patch(color='#f4d58d', label='Disco'),
        Patch(color='#bf0603', label='Bar')
        
    ]

    # Add legend to the plot
    legend = plt.legend(handles=legend_handles, loc='upper left', frameon=False, 
                        bbox_to_anchor=(0, 1.02, 1, 0.2), mode="expand", borderaxespad=0, ncol=4)
    
    for text in legend.get_texts():
        text.set_fontfamily('Times New Roman')
    
    #plt.tight_layout()
    plt.savefig("./results/" + type + "_province.png", dpi=900)
    plt.close()

def coffee_visualization(input_df_path, province, type):
    charging_df = pd.read_excel(input_df_path)
    charging_df = charging_df.dropna(subset=['lat'])
    charging_df = charging_df.astype({"lat":float, "lon":float})
    gdf_province = gpd.read_file("./data/shape_data/"+ province + "/" + province + ".shp")
    gdf_china = gpd.read_file("./data/shape_data/China/chn_admbnda_adm1_ocha_2020.shp")
    charging_gdf = df_to_gdf(charging_df, "lon", "lat")
    
    # Plot for china
    plt.figure(figsize=(20, 15))
    gdf_china.boundary.plot(linewidth=0.5, color="#adb5bd", zorder=1)
    bounds = gdf_china.total_bounds
    ax = plt.gca()
    
    # Set the aspect of the plot to be equal
    ax.set_aspect('equal')
    extend = 0
    ax.set_xlim(bounds[0]-extend, bounds[2]+extend)
    ax.set_ylim(bounds[1]-extend, bounds[3]+extend)
    ax.axis('off')

    num_ratio = 0.04

    for index, row in charging_gdf.iterrows():
        if row["coffee"] == "LUCKIN":
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#242170', linewidths=0, edgecolor=None, alpha=0.5)
        elif row["coffee"] == "COTTI":
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#ea5a4f', linewidths=0, edgecolor=None, alpha=0.5)
        else:
            pass
    
    # Define custom legend handles and labels
    legend_handles = [
        Patch(color='#242170', label='LUCKIN'),
        Patch(color='#ea5a4f', label='COTTI'),
    ]
    
    # Add legend to the plot
    legend = plt.legend(handles=legend_handles, loc='upper left', frameon=False, 
                        bbox_to_anchor=(0, 1.02, 1, 0.2), mode="expand", borderaxespad=0, ncol=2)
    
    for text in legend.get_texts():
        text.set_fontfamily('Times New Roman')

    #plt.tight_layout()
    plt.savefig("./results/" + type + "_cn.png", dpi=900)
    plt.close()
    
    # Plot for province
    charging_province = gpd.sjoin(charging_gdf, gdf_province, how='inner', op='within')
    plt.figure(figsize=(20, 15))
    gdf_province.boundary.plot(linewidth=0.5, color="#adb5bd", zorder=1)
    bounds = gdf_province.total_bounds
    ax = plt.gca()
    
    # Set the aspect of the plot to be equal
    ax.set_aspect('equal')
    extend = 0
    ax.set_xlim(bounds[0]-extend, bounds[2]+extend)
    ax.set_ylim(bounds[1]-extend, bounds[3]+extend)
    ax.axis('off')
    
    num_ratio = 0.1
    
    for index, row in charging_gdf.iterrows():
        if row["coffee"] == "LUCKIN":
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#242170', linewidths=0, edgecolor=None, alpha=0.5)
        elif row["coffee"] == "COTTI":
            ax.scatter(row.geometry.x, row.geometry.y, s=20*num_ratio, color='#ea5a4f', linewidths=0, edgecolor=None, alpha=0.5)
        else:
            pass
    
    # Define custom legend handles and labels
    legend_handles = [
        Patch(color='#242170', label='LUCKIN'),
        Patch(color='#ea5a4f', label='COTTI'),
    ]

    # Add legend to the plot
    legend = plt.legend(handles=legend_handles, loc='upper left', frameon=False, 
                        bbox_to_anchor=(0, 1.02, 1, 0.2), mode="expand", borderaxespad=0, ncol=2)
    
    for text in legend.get_texts():
        text.set_fontfamily('Times New Roman')
    
    #plt.tight_layout()
    plt.savefig("./results/" + type + "_province.png", dpi=900)
    plt.close()

if __name__ == "__main__":

    #base_website_no_api = "https://ditu.amap.com/service/poiInfo?query_type=TQUERY&pagesize={pagesize}&pagenum={pagenum}&zoom={zoom}&city={city}&keywords=%E5%85%85%E7%94%B5%E6%A1%A9#/"

    json_save_path = "./results/gaode/json/"
    haha_json_save_path = "./results/gaode_haha/json/"
    entertain_json_save_path = "./results/gaode_entertain/json/"
    luckin_save_path = "./results/gaode_luckin_coffee/json/"
    cotti_save_path = "./results/gaode_cotti_coffee/json/"
    adcode_list = adminstration_code_data("./data/china_city.json")
    total_adcode = len(adcode_list)
    
    # Get the data using Gaode api
    """
    for counter in range(2843, len(adcode_list)):
        print(counter, "/", total_adcode, "  ", adcode_list[counter])
        gaode_charging_data_obtain_api(adcode_list[counter])
        print("___________________________________________________________")
    """
    
    # Json data aggregate
    """
    gaode_df = pd.DataFrame()
    parent_list = []
    address_list = []
    pname_list = []
    rating_list = []
    cityname_list = []
    type_list = []
    typecode_list = []
    shopinfo_list = []
    adname_list = []
    name_list = []
    lat_list = []
    lon_list = []
    tel_list = []
    shopid_list = []
    id_list = []
    
    # Merge the json files into dataframe
    for counter in range(total_adcode):
        print(counter, "/", total_adcode)
        temp_json_path = json_save_path + adcode_list[counter] + ".json"
        with open(temp_json_path, 'r') as f:
            temp_json_data = json.load(f)
        
        for entry in temp_json_data:
            
            if len(entry) != 0:
                # Parent
                parent = entry.get("parent")
                if isinstance(parent, str):
                    parent_list.append(parent)
                else:
                    parent_list.append("")

                # Address
                address = entry.get("address")
                if isinstance(address, str):
                    address_list.append(address)
                else:
                    address_list.append("")
                
                # pname
                pname = entry.get("pname")
                if isinstance(pname, str):
                    pname_list.append(pname)
                else:
                    pname_list.append("")
                
                # rating
                rating = entry.get("biz_ext").get("rating")
                if isinstance(rating, str):
                    rating_list.append(rating)
                else:
                    rating_list.append("")
                
                # cityname
                cityname = entry.get("cityname")
                if isinstance(cityname, str):
                    cityname_list.append(cityname)
                else:
                    cityname_list.append("")
                
                # type
                type = entry.get("type")
                if isinstance(type, str):
                    type_list.append(type)
                else:
                    type_list.append("")
                
                # typecode
                typecode = entry.get("typecode")
                if isinstance(typecode, str):
                    typecode_list.append(typecode)
                else:
                    typecode_list.append("")
                    
                # shopinfo
                shopinfo = entry.get("shopinfo")
                if isinstance(shopinfo, str):
                    shopinfo_list.append(shopinfo)
                else:
                    shopinfo_list.append("")
                
                # adname
                adname = entry.get("adname")
                if isinstance(adname, str):
                    adname_list.append(adname)
                else:
                    adname_list.append("")
                
                # name
                name = entry.get("name")
                if isinstance(name, str):
                    name_list.append(name)
                else:
                    name_list.append("")
                    
                # lat lon
                location = entry.get("location")
                if isinstance(location, str):
                    lat, lon = location.split(",")
                    lat_list.append(float(lat))
                    lon_list.append(float(lon))
                else:
                    lat_list.append("")
                    lon_list.append("")
                    
                # tel
                tel = entry.get("tel")
                if isinstance(tel, str):
                    tel_list.append(tel)
                else:
                    tel_list.append("")
                    
                # shopid
                shopid = entry.get("shopid")
                if isinstance(shopid, str):
                    shopid_list.append(shopid)
                else:
                    shopid_list.append("")
                    
                # id
                id = entry.get("id")
                if isinstance(id, str):
                    id_list.append(id)
                else:
                    id_list.append("")
                
            else:
                pass
                

    gaode_df["parent"] = parent_list
    gaode_df["id"] = id_list
    gaode_df["name"] = name_list
    gaode_df["adname"] = adname_list
    gaode_df["pname"] = pname_list
    gaode_df["address"] = address_list
    gaode_df["cityname"] = cityname_list
    gaode_df["type"] = type_list
    gaode_df["typecode"] = typecode_list
    gaode_df["shopinfo"] = shopinfo_list
    gaode_df["shopid"] = shopid_list
    gaode_df["tel"] = tel_list
    gaode_df["rating"] = rating_list
    gaode_df["lat"] = lat_list
    gaode_df["lon"] = lon_list

    print(gaode_df)
    gaode_df.to_excel("./results/gaode.xlsx", index=False)
    visualization("./results/gaode.xlsx", "Guangxi")
    """
    #obtain_detail_by_id("./results/gaode.xlsx")
    
    
    # Get haha data
    """
    for counter in range(1724, len(adcode_list)):
        print(counter, "/", total_adcode, "  ", adcode_list[counter])
        gaode_haha_data_obtain_api(adcode_list[counter])
        print("___________________________________________________________")
    """
    
    # Json data aggregate for haha
    """
    haha_df = pd.DataFrame()
    parent_list = []
    address_list = []
    pname_list = []
    
    cost_list = []
    opentime2_list = []
    rating_list = []
    open_time_list = []
    
    cityname_list = []
    type_list = []
    typecode_list = []
    shopinfo_list = []
    adname_list = []
    name_list = []
    lat_list = []
    lon_list = []
    tel_list = []
    shopid_list = []
    id_list = []
    
    # Merge the json files into dataframe
    for counter in range(total_adcode):
        print(counter, "/", total_adcode)
        temp_json_path = haha_json_save_path + adcode_list[counter] + ".json"
        with open(temp_json_path, 'r') as f:
            temp_json_data = json.load(f)
        
        for entry in temp_json_data:
            
            if len(entry) != 0:
                # Parent
                parent = entry.get("parent")
                if isinstance(parent, str):
                    parent_list.append(parent)
                else:
                    parent_list.append("")

                # Address
                address = entry.get("address")
                if isinstance(address, str):
                    address_list.append(address)
                else:
                    address_list.append("")
                
                # pname
                pname = entry.get("pname")
                if isinstance(pname, str):
                    pname_list.append(pname)
                else:
                    pname_list.append("")
                
                # cost, rating
                biz_ext = entry.get("biz_ext")
                
                cost = biz_ext.get("cost")
                if isinstance(cost, str):
                    cost_list.append(cost)
                else:
                    cost_list.append("")
                    
                rating = biz_ext.get("rating")
                if isinstance(rating, str):
                    rating_list.append(rating)
                else:
                    rating_list.append("")
                    
                open_time = biz_ext.get("open_time")
                if isinstance(open_time, str):
                    open_time_list.append(open_time)
                else:
                    open_time_list.append("")

                opentime2 = biz_ext.get("opentime2")
                if isinstance(opentime2, str):
                    opentime2_list.append(opentime2)
                else:
                    opentime2_list.append("")

                # cityname
                cityname = entry.get("cityname")
                if isinstance(cityname, str):
                    cityname_list.append(cityname)
                else:
                    cityname_list.append("")
                
                # type
                type = entry.get("type")
                if isinstance(type, str):
                    type_list.append(type)
                else:
                    type_list.append("")
                
                # typecode
                typecode = entry.get("typecode")
                if isinstance(typecode, str):
                    typecode_list.append(typecode)
                else:
                    typecode_list.append("")
                    
                # shopinfo
                shopinfo = entry.get("shopinfo")
                if isinstance(shopinfo, str):
                    shopinfo_list.append(shopinfo)
                else:
                    shopinfo_list.append("")
                
                # adname
                adname = entry.get("adname")
                if isinstance(adname, str):
                    adname_list.append(adname)
                else:
                    adname_list.append("")
                
                # name
                name = entry.get("name")
                if isinstance(name, str):
                    name_list.append(name)
                else:
                    name_list.append("")
                    
                # lat lon
                location = entry.get("location")
                if isinstance(location, str):
                    lon, lat = location.split(",")
                    lat_list.append(float(lat))
                    lon_list.append(float(lon))
                else:
                    lat_list.append("")
                    lon_list.append("")
                    
                # tel
                tel = entry.get("tel")
                if isinstance(tel, str):
                    tel_list.append(tel)
                else:
                    tel_list.append("")
                    
                # shopid
                shopid = entry.get("shopid")
                if isinstance(shopid, str):
                    shopid_list.append(shopid)
                else:
                    shopid_list.append("")
                    
                # id
                id = entry.get("id")
                if isinstance(id, str):
                    id_list.append(id)
                else:
                    id_list.append("")
                
            else:
                pass
                
    haha_df["parent"] = parent_list
    haha_df["id"] = id_list
    haha_df["name"] = name_list
    haha_df["adname"] = adname_list
    haha_df["pname"] = pname_list
    haha_df["address"] = address_list
    haha_df["cityname"] = cityname_list
    haha_df["type"] = type_list
    haha_df["typecode"] = typecode_list
    haha_df["shopinfo"] = shopinfo_list
    haha_df["shopid"] = shopid_list
    haha_df["tel"] = tel_list
    haha_df["rating"] = rating_list
    haha_df["lat"] = lat_list
    haha_df["lon"] = lon_list
    haha_df["cost"] = cost_list
    haha_df["opentime2"] = opentime2_list
    haha_df["open_time"] = open_time_list

    print(haha_df)
    haha_df.to_excel("./results/haha.xlsx", index=False)
    """
    
    #visualization("./results/haha.xlsx", "Guangxi", "food")
    
    # Json data aggregate for entertain
    """
    haha_df = pd.DataFrame()
    parent_list = []
    address_list = []
    pname_list = []
    
    cost_list = []
    rating_list = []
    
    cityname_list = []
    type_list = []
    typecode_list = []
    shopinfo_list = []
    adname_list = []
    name_list = []
    lat_list = []
    lon_list = []
    tel_list = []
    shopid_list = []
    id_list = []
    
    # Merge the json files into dataframe
    for counter in range(total_adcode):
        print(counter, "/", total_adcode)
        temp_json_path = entertain_json_save_path + adcode_list[counter] + ".json"
        with open(temp_json_path, 'r') as f:
            temp_json_data = json.load(f)
        
        for entry in temp_json_data:
            
            if len(entry) != 0:
                # Parent
                parent = entry.get("parent")
                if isinstance(parent, str):
                    parent_list.append(parent)
                else:
                    parent_list.append("")

                # Address
                address = entry.get("address")
                if isinstance(address, str):
                    address_list.append(address)
                else:
                    address_list.append("")
                
                # pname
                pname = entry.get("pname")
                if isinstance(pname, str):
                    pname_list.append(pname)
                else:
                    pname_list.append("")
                
                # cost, rating
                biz_ext = entry.get("biz_ext")
                
                cost = biz_ext.get("cost")
                if isinstance(cost, str):
                    cost_list.append(cost)
                else:
                    cost_list.append("")
                    
                rating = biz_ext.get("rating")
                if isinstance(rating, str):
                    rating_list.append(rating)
                else:
                    rating_list.append("")
                    

                # cityname
                cityname = entry.get("cityname")
                if isinstance(cityname, str):
                    cityname_list.append(cityname)
                else:
                    cityname_list.append("")
                
                # type
                type = entry.get("type")
                if isinstance(type, str):
                    type_list.append(type)
                else:
                    type_list.append("")
                
                # typecode
                typecode = entry.get("typecode")
                if isinstance(typecode, str):
                    typecode_list.append(typecode)
                else:
                    typecode_list.append("")
                    
                # shopinfo
                shopinfo = entry.get("shopinfo")
                if isinstance(shopinfo, str):
                    shopinfo_list.append(shopinfo)
                else:
                    shopinfo_list.append("")
                
                # adname
                adname = entry.get("adname")
                if isinstance(adname, str):
                    adname_list.append(adname)
                else:
                    adname_list.append("")
                
                # name
                name = entry.get("name")
                if isinstance(name, str):
                    name_list.append(name)
                else:
                    name_list.append("")
                    
                # lat lon
                location = entry.get("location")
                if isinstance(location, str):
                    lon, lat = location.split(",")
                    lat_list.append(float(lat))
                    lon_list.append(float(lon))
                else:
                    lat_list.append("")
                    lon_list.append("")
                    
                # tel
                tel = entry.get("tel")
                if isinstance(tel, str):
                    tel_list.append(tel)
                else:
                    tel_list.append("")
                    
                # shopid
                shopid = entry.get("shopid")
                if isinstance(shopid, str):
                    shopid_list.append(shopid)
                else:
                    shopid_list.append("")
                    
                # id
                id = entry.get("id")
                if isinstance(id, str):
                    id_list.append(id)
                else:
                    id_list.append("")
                
            else:
                pass
                
    haha_df["parent"] = parent_list
    haha_df["id"] = id_list
    haha_df["name"] = name_list
    haha_df["adname"] = adname_list
    haha_df["pname"] = pname_list
    haha_df["address"] = address_list
    haha_df["cityname"] = cityname_list
    haha_df["type"] = type_list
    haha_df["typecode"] = typecode_list
    haha_df["shopinfo"] = shopinfo_list
    haha_df["shopid"] = shopid_list
    haha_df["tel"] = tel_list
    haha_df["rating"] = rating_list
    haha_df["lat"] = lat_list
    haha_df["lon"] = lon_list
    haha_df["cost"] = cost_list

    print(haha_df)
    haha_df.to_excel("./results/entertain.xlsx", index=False)
    """
    
    #entertain_visualization("./results/entertain.xlsx", "Guangxi", "entertain")
    
    # Luckin coffee data obtain
    """
    for counter in range(1572, len(adcode_list)):
        print(counter, "/", total_adcode, "  ", adcode_list[counter])
        gaode_cotti_data_obtain_api(adcode_list[counter])
        print("___________________________________________________________")
    """
    
    """
    haha_df = pd.DataFrame()
    parent_list = []
    address_list = []
    pname_list = []
    
    cost_list = []
    rating_list = []
    
    cityname_list = []
    type_list = []
    typecode_list = []
    shopinfo_list = []
    adname_list = []
    name_list = []
    lat_list = []
    lon_list = []
    tel_list = []
    shopid_list = []
    id_list = []
    
    # Merge the json files into dataframe
    for counter in range(total_adcode):
        print(counter, "/", total_adcode)
        temp_json_path = cotti_save_path + adcode_list[counter] + ".json"
        with open(temp_json_path, 'r') as f:
            temp_json_data = json.load(f)
        
        for entry in temp_json_data:
            
            if len(entry) != 0:
                # Parent
                parent = entry.get("parent")
                if isinstance(parent, str):
                    parent_list.append(parent)
                else:
                    parent_list.append("")

                # Address
                address = entry.get("address")
                if isinstance(address, str):
                    address_list.append(address)
                else:
                    address_list.append("")
                
                # pname
                pname = entry.get("pname")
                if isinstance(pname, str):
                    pname_list.append(pname)
                else:
                    pname_list.append("")
                
                # cost, rating
                biz_ext = entry.get("biz_ext")
                
                cost = biz_ext.get("cost")
                if isinstance(cost, str):
                    cost_list.append(cost)
                else:
                    cost_list.append("")
                    
                rating = biz_ext.get("rating")
                if isinstance(rating, str):
                    rating_list.append(rating)
                else:
                    rating_list.append("")
                    

                # cityname
                cityname = entry.get("cityname")
                if isinstance(cityname, str):
                    cityname_list.append(cityname)
                else:
                    cityname_list.append("")
                
                # type
                type = entry.get("type")
                if isinstance(type, str):
                    type_list.append(type)
                else:
                    type_list.append("")
                
                # typecode
                typecode = entry.get("typecode")
                if isinstance(typecode, str):
                    typecode_list.append(typecode)
                else:
                    typecode_list.append("")
                    
                # shopinfo
                shopinfo = entry.get("shopinfo")
                if isinstance(shopinfo, str):
                    shopinfo_list.append(shopinfo)
                else:
                    shopinfo_list.append("")
                
                # adname
                adname = entry.get("adname")
                if isinstance(adname, str):
                    adname_list.append(adname)
                else:
                    adname_list.append("")
                
                # name
                name = entry.get("name")
                if isinstance(name, str):
                    name_list.append(name)
                else:
                    name_list.append("")
                    
                # lat lon
                location = entry.get("location")
                if isinstance(location, str):
                    lon, lat = location.split(",")
                    lat_list.append(float(lat))
                    lon_list.append(float(lon))
                else:
                    lat_list.append("")
                    lon_list.append("")
                    
                # tel
                tel = entry.get("tel")
                if isinstance(tel, str):
                    tel_list.append(tel)
                else:
                    tel_list.append("")
                    
                # shopid
                shopid = entry.get("shopid")
                if isinstance(shopid, str):
                    shopid_list.append(shopid)
                else:
                    shopid_list.append("")
                    
                # id
                id = entry.get("id")
                if isinstance(id, str):
                    id_list.append(id)
                else:
                    id_list.append("")
                
            else:
                pass
                
    haha_df["parent"] = parent_list
    haha_df["id"] = id_list
    haha_df["name"] = name_list
    haha_df["adname"] = adname_list
    haha_df["pname"] = pname_list
    haha_df["address"] = address_list
    haha_df["cityname"] = cityname_list
    haha_df["type"] = type_list
    haha_df["typecode"] = typecode_list
    haha_df["shopinfo"] = shopinfo_list
    haha_df["shopid"] = shopid_list
    haha_df["tel"] = tel_list
    haha_df["rating"] = rating_list
    haha_df["lat"] = lat_list
    haha_df["lon"] = lon_list
    haha_df["cost"] = cost_list

    print(haha_df)
    haha_df.to_excel("./results/cotti_coffee.xlsx", index=False)
    """
    """
    luck_df = pd.read_excel("./results/luckin_coffee.xlsx")
    luck_df["coffee"] = "LUCKIN"
    cotti_df = pd.read_excel("./results/cotti_coffee.xlsx")
    cotti_df["coffee"] = "COTTI"
    
    coffee_df = pd.concat([luck_df, cotti_df], axis=0).reset_index(drop=True)
    coffee_df.to_excel("./results/coffee.xlsx", index=False)
    """
    coffee_visualization("./results/coffee.xlsx", "Guangxi", "coffee")
