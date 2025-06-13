from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import random
import csv
from datetime import datetime

class EasyApplyLinkedin:
    def __init__(self, data):
        """Parameter Initialization"""
        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        chrome_service = Service(data['driver_path'])
        self.driver = webdriver.Chrome(service=chrome_service)

    def login_linkedin(self):
        '''Login to linkedin profile and go to jobs page after 2 seconds'''
        self.driver.get("https://www.linkedin.com/login")
        login_email = self.driver.find_element(By.NAME, "session_key")
        login_email.clear()
        login_email.send_keys(self.email)
        login_password = self.driver.find_element(By.NAME, "session_password")
        login_password.clear()
        login_password.send_keys(self.password)
        login_password.send_keys(Keys.RETURN)
        time.sleep(2)  # Wait 2 seconds before navigating to Jobs page
        self.driver.get("https://www.linkedin.com/jobs/")  # Go directly to Jobs page
