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
        # Number of countries
        country_num = len(self.country_list)
        
        for i in range(0, country_num):
            temp_country = self.country_list[i]
            print(temp_country, str(i), "/", str(country_num))
            self.temp_supercharger_website = self.supercharger_list[i]
            self.temp_destination_website = self.destination_list[i]
            
            self.temp_save_path = self.result_base_path + "/" + temp_country + "/"
            # Create folder
            if not os.path.exists(self.temp_save_path):
                os.mkdir(self.temp_save_path)

            # Superchargers
            if self.temp_supercharger_website != None:
                self._cn_links_obtain(self.temp_supercharger_website, self.temp_save_path + "supercharger")
            else:
                pass
            
            # Destination chargers
            if self.temp_destination_website != None:
                self._cn_links_obtain(self.temp_destination_website, self.temp_save_path + "destination")
            else:
                pass
            
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
            address, locality, lat, lon, info = self._cn_info_aggregate(self.link_list[counter])
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

    def _cn_info_aggregate(self, link):
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
        
    def _driver_close(self):
        self.driver.close()

      
if __name__ == "__main__":
    
    # Crawl the global data
    crawler = TESLA_crawler()
    crawler.obtain_country_names()
    crawler.global_charger_crawl()
    
    # Crawl the china data
    