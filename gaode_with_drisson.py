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


if __name__ == "__main__":    
    def handle_detail(poi_list):
        try:
            base_url = "https://amap.com/place/"
            page = ChromiumPage()
            page.get(base_url)  # 访问网址，这行产生的数据包不监听           
            page.listen.start('amap.com/detail/get/detail')  # 开始监听，指定获取包含该文本的数据包        
            for poi in poi_list:            
                poi_id = poi['id']            
                page.get(base_url + poi_id)            
                res = page.listen.wait()  # 等待并获取一个数据包            
                detail_json = res.response.body            
                detail_json = detail_json['data']            
                db.update(table='gaode_pois',                      
                        data={'detail_json_data': json.dumps(detail_json)},                      
                        condition=f" poi_id = '{poi_id}'")
        except Exception as e:
            print(e)   

    def to_excel():
        detail_list = db.query("select poi_id,detail_json_data,create_time from gaode_pois")    
        result = []    
        for detail in detail_list:        
            detail_json_data = json.loads(detail['detail_json_data'])           
            poi_id = detail['poi_id']        
            create_time = detail['create_time']        
            city_name = detail_json_data['base']['city_name']        
            name = detail_json_data['base']['name']        
            address = detail_json_data['base']['address']        
            brand_desc = detail_json_data['charging']['brand_desc']        
            charge_price = detail_json_data['charging']['charge_price']        
            price_parking = detail_json_data['deep']['price_parking']        
            result.append({        
                           'city_name': city_name,            
                           'poi_id': poi_id,            
                           'name': name,            
                           'address': address,            
                           'brand_desc': brand_desc,            
                           'charge_price': charge_price,            
                           'price_parking': price_parking,            
                           'create_time': create_time})    
            df = pd.DataFrame(result)    
            df.columns = ['城市', 'id', '名称', '地址', '品牌', '价格', '价格标记', '采集时间']    
            output_path = ".xlsx"
            df.to_excel(output_path, index=False)    
