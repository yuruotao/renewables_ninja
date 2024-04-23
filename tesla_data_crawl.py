# coding: utf-8
import pandas as pd
import numpy as np
import os
from selenium import webdriver
import selenium.common
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import selenium
import time
import re
import requests

def get_lat_lon_from_address(address):
    # API endpoint for Baidu Maps Geocoding API
    url = "http://api.map.baidu.com/geocoding/v3/"

    # Parameters for the API request
    params = {
        "address": address,
        "output": "json",
        "ak": "mTeb6B0dqzwPH8cCZynBsFrqHdCwGlO7"
    }

    # Make the API request
    response = requests.get(url, params=params)
    data = response.json()

    # Extract latitude and longitude from the response
    if data["status"] == 0:
        location = data["result"]["location"]
        lat = location["lat"]
        lon = location["lng"]
        return lat, lon
    else:
        print("Geocoding request failed. Error message:", data["message"])
        return None, None

class baidu_driver:
    def __init__(self):
        # Initiate the web driver and options
        if not os.path.exists('./web_driver'):
            os.mkdir('./web_driver')
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(version="110.0.5481.77").install()))
        self.driver_path = './web_driver/chromedriver.exe'
        
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        self.options.add_argument("--window-size=2560,1440")
        self.options.use_chromium = True
        
        self.service = ChromeService(executable_path=self.driver_path)
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

class TESLA_crawler:
    def __init__(self):
        # Initiate the web driver and options
        if not os.path.exists('./web_driver'):
            os.mkdir('./web_driver')
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(version="110.0.5481.77").install()))
        self.driver_path = './web_driver/chromedriver.exe'
        
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        self.options.add_argument("--window-size=2560,1440")
        self.options.use_chromium = True
        
        self.service = ChromeService(executable_path=self.driver_path)
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

        self.base_website = "https://www.tesla.com/en_GB/findus/list#/&cc=US"
        self.cn_base_website ="https://www.tesla.cn/findus/list#/"
        self.supercharger_base_website = "https://www.tesla.com/en_gb/findus/list/superchargers/"
        self.destination_base_website = "https://www.tesla.com/en_gb/findus/list/chargers/"
        self.result_base_path = "./results/tesla"
        self.cn_result_base_path = "./results/tesla_cn"
    
    # Global website methods
    def obtain_country_names(self):
        self.driver.minimize_window()
        self.driver.get(self.base_website)
        
        # Click the language button
        button = self.driver.find_element(By.ID, value="dx-nav-item--locale-selector")
        button.click()
        
        self.country_list = []
        self.supercharger_list = []
        self.destination_list = []
        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "setCountSize"))
        )
        
        for item in elements:
            self.country_list.append(item.text)
            
            nearest_div = item.find_element(By.XPATH, './following-sibling::div')
            div_text = nearest_div.text
            
            if "Superchargers" in div_text:
                self.supercharger_list.append(self.supercharger_base_website + item.text + "#/")
            else:
                self.supercharger_list.append(None)
                
            if "Destination" in div_text:
                self.destination_list.append(self.destination_base_website + item.text + "#/")
            else:
                self.destination_list.append(None)
        
        print(self.country_list)
        #self.driver.close()
    
    def global_charger_crawl(self):
        # Number of countries
        country_num = len(self.country_list)
        
        for i in range(3, country_num):
            temp_country = self.country_list[i]
            print(temp_country, str(i), "/", str(country_num))
            self.temp_supercharger_website = self.supercharger_list[i].replace(" ", "+")
            self.temp_destination_website = self.destination_list[i].replace(" ", "+")
            
            self.temp_save_path = self.result_base_path + "/" + temp_country + "/"
            # Create folder
            if not os.path.exists(self.temp_save_path):
                os.mkdir(self.temp_save_path)

            # Superchargers
            if self.temp_supercharger_website != None:
                self._links_obtain(self.temp_supercharger_website, self.temp_save_path + "supercharger")
            else:
                pass
            
            # Destination chargers
            if self.temp_destination_website != None:
                self._links_obtain(self.temp_destination_website, self.temp_save_path + "destination")
            else:
                pass
            
        self._driver_close()
    
    def _links_obtain(self, website, save_path):
        self.driver.minimize_window()
        self.driver.get(website)
        
        current_url = self.driver.current_url
        if website in current_url:
            # Click the language button
            try:
                button = self.driver.find_element(By.ID, value="dx-nav-item--locale-selector")
                button.click()
            except selenium.common.exceptions.NoSuchElementException:
                pass
            
            self.link_list = []
            divs_elements = WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "anchor-container"))
            )
            
            for div_element in divs_elements:
                # Find the <a> element within the <div> element
                a_element = div_element.find_element(By.TAG_NAME, value="a")

                # Extract the value of the "href" attribute from the <a> element
                href_value = a_element.get_attribute("href")
                self.link_list.append(href_value)
            
            address_list = []
            locality_list = []
            lat_list = []
            lon_list = []
            info_list = []
            
            counter = 0
            link_num = len(self.link_list)
            for counter in range(0, link_num):
                print(str(counter), "/", link_num)
                print(self.link_list[counter])
                address, locality, lat, lon, info = self._info_aggregate(self.link_list[counter])
                print(address, locality, lat, lon, info)
                time.sleep(1)
                address_list.append(address)
                locality_list.append(locality)
                lat_list.append(lat)
                lon_list.append(lon)
                info_list.append(info)

            country_df = pd.DataFrame({"address":address_list, 
                                    "locality":locality_list,
                                    "lat":lat_list,
                                    "lon":lon_list,
                                    "info":info_list,
                                    "link":self.link_list})
            country_df.to_excel(save_path + ".xlsx", index=False)
        else:
            pass

    def _info_aggregate(self, link):
        self.driver.minimize_window()
        self.driver.get(link)
        
        current_url = self.driver.current_url
        if link in current_url:
            # Click the language button
            try:
                button = self.driver.find_element(By.ID, value="dx-nav-item--locale-selector")
                button.click()
            except selenium.common.exceptions.NoSuchElementException:
                pass
            
            # Get the elements
            vcard_elements = WebDriverWait(self.driver, 100).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "vcard"))
            )
            vcard_element = vcard_elements[0]
            
            try:
                address_element = vcard_element.find_element(By.CLASS_NAME, value="street-address")
                address = address_element.text.replace("\n", " ")
            except selenium.common.exceptions.NoSuchElementException:
                address = np.nan
            
            try:
                locality_element = vcard_element.find_element(By.CLASS_NAME, value="locality")
                locality = locality_element.text.replace("\n", " ")
            except selenium.common.exceptions.NoSuchElementException:
                locality = np.nan
            
            driving_directions = "Driving Directions"
            try:
                lat_lon_element = vcard_element.find_element(By.XPATH, value=f"//a[contains(text(), '{driving_directions}')]")
                lat_lon = lat_lon_element.get_attribute("href").split("=")[-1].split(",")
                lat = float(lat_lon[0])
                lon = float(lat_lon[1])
            except selenium.common.exceptions.NoSuchElementException:
                lat = np.nan
                lon = np.nan
                
            charging = "Charging"
            try:
                info_element = vcard_element.find_element(By.XPATH, value=f"//p[contains(text(), '{charging}')]")
                info = info_element.text.replace("\n", " ").lstrip("Charging ")
            except selenium.common.exceptions.NoSuchElementException:
                info = np.nan
            
            return address, locality, lat, lon, info
        else:
            return np.nan, np.nan, np.nan, np.nan, np.nan
        
    # The lower methods are for the chinese version website
    def cn_charger_crawl(self):
        self.driver.minimize_window()
        self.driver.get(self.cn_base_website)
        
        # Click the language button
        try:
            button = self.driver.find_element(By.ID, value="dx-nav-item--locale-selector")
            button.click()
        except selenium.common.exceptions.NoSuchElementException:
            pass
        
        self.cn_supercharger_list = []
        self.cn_destination_list = []
        row_elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "row"))
        )
        
        for row_element in row_elements:
            # Detect the supercharge and destination charge
            try:
                h2_element = row_element.find_element(By.TAG_NAME, value="h2")
                if h2_element.text == "Tesla 超级充电站":
                    a_elements = row_element.find_elements(By.TAG_NAME, value="a")
                    for a_element in a_elements:
                        self.cn_supercharger_list.append(a_element.get_attribute("href"))
                elif h2_element.text == "Tesla 目的地充电":
                    a_elements = row_element.find_elements(By.TAG_NAME, value="a")
                    for a_element in a_elements:
                        self.cn_destination_list.append(a_element.get_attribute("href"))
                else:
                    pass
            except selenium.common.exceptions.NoSuchElementException:
                pass
        
        cn_super_province_num = len(self.cn_supercharger_list)
        cn_destination_province_num = len(self.cn_destination_list)

        # Superchargers
        for i in range(8, cn_super_province_num):
            print(i+1, "/", cn_super_province_num)
            temp_website = self.cn_supercharger_list[i]
            self._cn_links_obtain(temp_website, self.cn_result_base_path + "/supercharger")

        # Destination chargers
        for j in range(0, cn_destination_province_num):
            print(j+1, "/", cn_destination_province_num)
            temp_website = self.cn_supercharger_list[j]
            self._cn_links_obtain(temp_website, self.cn_result_base_path + "/destination")
            
        self._driver_close()
    
    def _cn_links_obtain(self, website, save_path):
        self.driver.minimize_window()
        self.driver.get(website)
        
        # Click the language button
        try:
            button = self.driver.find_element(By.ID, value="dx-nav-item--locale-selector")
            button.click()
        except selenium.common.exceptions.NoSuchElementException:
            pass
        
        self.link_list = []
        divs_elements = WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "anchor-container"))
        )
        
        h1_elements = WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "h1"))
        )
        h1_element = h1_elements[1]
        province = h1_element.text.split(" - ")[1]
        
        for div_element in divs_elements:
            # Find the <a> element within the <div> element
            a_element = div_element.find_element(By.TAG_NAME, value="a")

            # Extract the value of the "href" attribute from the <a> element
            href_value = a_element.get_attribute("href")
            self.link_list.append(href_value)
        
        name_list = []
        address_list = []
        locality_list = []
        lat_lon_list = []
        operate_time_list = []
        charging_power_list = []
        charging_num_list = []
        table_list = []
        
        link_num = len(self.link_list)
        for counter in range(0, link_num):
            print(str(counter+1), "/", link_num)
            print(self.link_list[counter])
            name, address, locality, lat_lon, operate_time, charging_power, charging_num, table = self._cn_info_aggregate(self.link_list[counter].replace("zh_cn/", ""))
            print(name, address, locality, lat_lon, operate_time, charging_power, charging_num, table)
            
            name_list.append(name)
            address_list.append(address)
            locality_list.append(locality)
            lat_lon_list.append(lat_lon)
            operate_time_list.append(operate_time)
            charging_power_list.append(charging_power)
            charging_num_list.append(charging_num)
            table_list.append(table)

        country_df = pd.DataFrame({"name":name_list,
                                    "address":address_list, 
                                "locality":locality_list,
                                "lat_lon":lat_lon_list,
                                "operate_time":operate_time_list,
                                "charging_power":charging_power_list,
                                "charging_num":charging_num_list,
                                "table":table_list,
                                "link":self.link_list})
        country_df.to_excel(save_path + province + ".xlsx", index=False)

    def _cn_info_aggregate(self, link):
        self.driver.minimize_window()
        self.driver.get(link)
        
        # Click the language button
        try:
            button = self.driver.find_element(By.ID, value="dx-nav-item--locale-selector")
            button.click()
        except selenium.common.exceptions.NoSuchElementException:
            pass
        
        # Get the elements
        vcard_elements = WebDriverWait(self.driver, 100).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "vcard"))
        )
        vcard_element = vcard_elements[0]
        
        # Name
        try:
            name_element = vcard_element.find_element(By.CLASS_NAME, value="common-name")
            name = name_element.text.replace("\n", " ")
        except selenium.common.exceptions.NoSuchElementException:
            name = np.nan
        
        # Address
        try:
            address_element = vcard_element.find_element(By.CLASS_NAME, value="street-address")
            address = address_element.text.replace("\n", " ")
        except selenium.common.exceptions.NoSuchElementException:
            address = np.nan
        
        # Locality
        try:
            locality_element = vcard_element.find_element(By.CLASS_NAME, value="locality")
            locality = locality_element.text.replace("\n", " ")
        except selenium.common.exceptions.NoSuchElementException:
            locality = np.nan
        
        # Lat lon link
        driving_directions = "行车路线"
        try:
            lat_lon_element = vcard_element.find_element(By.XPATH, value=f"//a[contains(text(), '{driving_directions}')]")
            lat_lon = lat_lon_element.get_attribute("href")
        except selenium.common.exceptions.NoSuchElementException:
            lat_lon = np.nan
        
        # Operate time
        operate_time_str = "开放时间"
        try:
            operate_time_element = vcard_element.find_element(By.XPATH, value=f"//p[contains(normalize-space(), '{operate_time_str}')]")
            operate_time = operate_time_element.text.replace("\n", " ").lstrip("开放时间 ")
        except selenium.common.exceptions.NoSuchElementException:
            operate_time = np.nan
        
        # Charging
        try:
            vcard_text = vcard_element.text
            max_power_match = re.search(r'最大功率可达\s+(\d+\s*kW)', vcard_text)
            num_chargers_match = re.search(r'(\d+)\s*个超级充电桩', vcard_text)

            if max_power_match:
                max_power = max_power_match.group(1)
            else:
                max_power = np.nan

            if num_chargers_match:
                num_chargers = num_chargers_match.group(1)
            else:
                num_chargers = np.nan
        except selenium.common.exceptions.NoSuchElementException:
            max_power = np.nan
            num_chargers = np.nan
            
        # Table
        try:
            table_element = vcard_element.find_element(By.CLASS_NAME, value="tds-table-body")
            table = table_element.text
        except selenium.common.exceptions.NoSuchElementException:
            table = np.nan
        
        return name, address, locality, lat_lon, operate_time, max_power, num_chargers, table
        #else:
            #return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
        
    def _driver_close(self):
        self.driver.close()

      
if __name__ == "__main__":
    
    # Crawl the global data
    #crawler = TESLA_crawler()
    #crawler.obtain_country_names()
    #crawler.global_charger_crawl()
    
    # Crawl the china data
    crawler = TESLA_crawler()
    crawler.cn_charger_crawl()