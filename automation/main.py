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

    def job_search(self):
        """Searches for jobs based on keywords and location."""
        wait = WebDriverWait(self.driver, 15)
        search_keyword = wait.until(EC.presence_of_element_located((By.XPATH, "//input[starts-with(@id,'jobs-search-box-keyword')]")))
        search_keyword.clear()
        search_keyword.send_keys(self.keywords)
        time.sleep(3)
        search_location = wait.until(EC.presence_of_element_located((By.XPATH, "//input[starts-with(@id,'jobs-search-box-location')]")))
        search_location.clear()
        search_location.send_keys(self.location)
        time.sleep(3)
        search_location.send_keys(Keys.RETURN)

    def filter(self):
        """Applies the 'Easy Apply' filter."""
        try:
            easy_apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "searchFilter_applyWithLinkedin"))
            )
            easy_apply_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"❌ Easy Apply filter not found: {e}")
        time.sleep(2)

    def get_total_results(self):
        """Gets the total number of job results found."""
        try:
            results_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'jobs-search-results-list__subtitle')]//span"))
            )
            total_results = int(results_element.text.split()[0].replace(",", ""))
            print(f"🔎 Total job results found: {total_results}")
            return total_results
        except Exception as e:
            print(f"❌ Could not fetch total results count: {e}")
            return 0

    def extract_job_cards(self):
        """Extracts all job card elements from the current page by scrolling until all are loaded."""
        try:
            print("Scrolling to load all job cards...")
            
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.job-card-container--clickable")
            
            while True:
                self.driver.execute_script("arguments[0].scrollIntoView();", job_cards[-1])
                time.sleep(2)
                new_job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.job-card-container--clickable")
                if len(new_job_cards) == len(job_cards):
                    break
                job_cards = new_job_cards

            print(f"✓ All job cards loaded ({len(job_cards)} found).")
            return job_cards
        except Exception as e:
            print(f"❌ Could not find or scroll job cards list: {e}")
            return []
