from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import json
import time
import random
import csv
from datetime import datetime
from os.path import isfile
import os

class EasyApplyLinkedin:
    def __init__(self, data):
        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        # Initialize the Chrome driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window()
        # Lists to track application status
        self.successful_apps = []
        self.failed_apps = []

    def login_linkedin(self):
        """Navigates to LinkedIn and logs in."""
        self.driver.get("https://www.linkedin.com/login")
        time.sleep(2)
        login_email = self.driver.find_element(By.NAME, "session_key")
        login_email.clear()
        login_email.send_keys(self.email)
        login_password = self.driver.find_element(By.NAME, "session_password")
        login_password.clear()
        login_password.send_keys(self.password)
        login_password.send_keys(Keys.RETURN)
        print("Please log in manually if required (e.g., captcha). Waiting for 15 seconds...")
        time.sleep(15) # Wait for login and potential manual captcha
        self.driver.get("https://www.linkedin.com/jobs/")
