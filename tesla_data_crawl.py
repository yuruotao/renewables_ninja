import pandas as pd
import numpy as np
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


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
                self.supercharger_list.append(self.supercharger_base_website + item.text + "/")
            else:
                self.supercharger_list.append(None)
                
            if "Destination" in div_text:
                self.destination_list.append(self.destination_base_website + item.text + "/")
            else:
                self.destination_list.append(None)
        
        print(self.country_list)
        print(self.supercharger_list)
        print(self.destination_list)
        self.driver.quit()
    
    def global_charger_crawl(self):
        # Number of countries
        country_num = len(self.country_list)
        
        for i in range(country_num):
            temp_country = self.country_list[i]
            self.temp_supercharger_website = self.supercharger_list[i]
            self.temp_destination_website = self.destination_list[i]
            self.temp_supercharge_path = self.result_base_path + "/" + temp_country + "/supercharge/"
            self.temp_destination_path = self.result_base_path + "/" + temp_country + "/destination/"
            
            # Create folder
            if not os.path.exists(self.temp_supercharge_path):
                os.mkdir(self.temp_supercharge_path)
            if not os.path.exists(self.temp_destination_path):
                os.mkdir(self.temp_destination_path)

            # Superchargers
            if self.temp_supercharger_website != None:
                self._links_obtain(self.temp_supercharger_website, self.temp_supercharge_path)
            else:
                pass

            # Destination chargers
            if self.temp_destination_website != None:
                self._links_obtain(self.temp_destination_website, self.temp_destination_path)
            else:
                pass
    
    def _links_obtain(self, website, save_path):
        self.driver.minimize_window(website)
        self.driver.get()
        
        # Click the language button
        button = self.driver.find_element(By.ID, value="dx-nav-item--locale-selector")
        button.click()
        
        self.link_list = []
        divs_elements = WebDriverWait(self.driver, 10).until(
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
        
        for link in self.link_list:
            self._link_data_gather(link)
            
    def _link_data_gather(self, link, save_path):
        self.driver.minimize_window(link)
        self.driver.get()
        
        # Click the language button
        button = self.driver.find_element(By.ID, value="dx-nav-item--locale-selector")
        button.click()
        
        self.link_list = []
        divs_elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "anchor-container"))
        )
        
        for div_element in divs_elements:
            # Find the <a> element within the <div> element
            a_element = div_element.find_element(By.TAG_NAME, value="a")

            # Extract the value of the "href" attribute from the <a> element
            href_value = a_element.get_attribute("href")
            self.link_list.append(href_value)
    
    # The lower methods are for the chinese version website
    def cn_charger_crawl(self):
        self.driver.minimize_window()
        self.driver.get(self.cn_base_website)
        
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
                self.supercharger_list.append(self.supercharger_base_website + item.text + "/")
            else:
                self.supercharger_list.append(None)
                
            if "Destination" in div_text:
                self.destination_list.append(self.destination_base_website + item.text + "/")
            else:
                self.destination_list.append(None)
        
        print(self.country_list)
        print(self.supercharger_list)
        print(self.destination_list)
        self.driver.quit()
    
    def _cn_province_links_obtain(self, website):
        self.driver.minimize_window(website)
        self.driver.get()
        
        # Click the language button
        button = self.driver.find_element(By.ID, value="dx-nav-item--locale-selector")
        button.click()
        
        self.link_list = []
        divs_elements = WebDriverWait(self.driver, 10).until(
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
        
        for link in self.link_list:
            self._link_data_gather(link)
        
    def _cn_data_gather(self):
        self.driver.minimize_window()
        self.driver.get(self.cn_base_website)
        
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
                self.supercharger_list.append(self.supercharger_base_website + item.text + "/")
            else:
                self.supercharger_list.append(None)
                
            if "Destination" in div_text:
                self.destination_list.append(self.destination_base_website + item.text + "/")
            else:
                self.destination_list.append(None)
        
        print(self.country_list)
        print(self.supercharger_list)
        print(self.destination_list)
        self.driver.quit()

if __name__ == "__main__":
    
    # Crawl the global data
    crawler = TESLA_crawler()
    crawler.obtain_country_names()
    
    
    # Crawl the china data