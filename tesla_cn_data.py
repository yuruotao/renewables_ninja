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
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        self.options.use_chromium = True
        
        self.driver = webdriver.Chrome(executable_path = self.driver_path, options=self.options)

        
        self.base_website = "https://www.tesla.cn/findus/list#/"



    def obtain_sub_elements(self):
        
        return None

if __name__ == "__main__":
    
    crawler = TESLA_crawler()