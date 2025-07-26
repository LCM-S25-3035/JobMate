# this version is not working
from selenium import webdriver  
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import openai
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
        self.resume_path = data.get('resume_path', '')
        self.api_key = data.get('api_key', None)
        if self.api_key:
            openai.api_key = self.api_key
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.maximize_window()
        self.successful_apps = []
        self.failed_apps = []

    def login_linkedin(self):
        self.driver.get("https://www.linkedin.com/login")
        login_email = self.driver.find_element(By.NAME, "session_key")
        login_email.clear()
        login_email.send_keys(self.email)
        login_password = self.driver.find_element(By.NAME, "session_password")
        login_password.clear()
        login_password.send_keys(self.password)
        login_password.send_keys(Keys.RETURN)
        time.sleep(5)
        self.driver.get("https://www.linkedin.com/jobs/")

    def job_search(self):
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
        try:
            easy_apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "searchFilter_applyWithLinkedin"))
            )
            easy_apply_button.click()
            time.sleep(2)
        except Exception as e:
            print("❌ Easy Apply filter not found:", e)
        time.sleep(2)

    def get_total_results(self):
        try:
            results_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'jobs-search-results-list__subtitle')]//span"))
            )
            total_results = int(results_element.text.split()[0].replace(",", ""))
            print("🔎 Total job results found:", total_results)
            return total_results
        except Exception as e:
            print("❌ Could not fetch total results count:", e)
            return 0

    def extract_job_cards(self):
        try:
            job_cards = WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.job-card-container.relative.job-card-list.job-card-container--clickable"))
            )
            for card in job_cards:
                ActionChains(self.driver).move_to_element(card).perform()
                time.sleep(0.5)
            return job_cards
        except Exception as e:
            print("❌ Could not find job cards:", e)
            return []

    def paginate_and_apply(self):
        base_url = self.driver.current_url.split('&start=')[0]
        total_results = self.get_total_results()
        total_pages = (total_results // 25) + 1

        for start in range(0, total_pages * 25, 25):
            paginated_url = f"{base_url}&start={start}"
            self.driver.get(paginated_url)
            print(f"📄 Navigated to page starting at {start}")
            time.sleep(3)
            job_cards = self.extract_job_cards()

            for job in job_cards:
                self.submit_application(job)
                
      # ------------ LLM AGENT METHODS ------------

    def answer_field_with_llm(self, label, field_type):
        """Answer for inputs/textarea/selects via LLM or fallback mapping."""
        if self.api_key and label:
            try:
                prompt = f"You're applying for a job as Hazel Portia Elaine Santos. Given the field '{label}' (type: {field_type}), what is the most appropriate value to enter in a real application? Use a professional, direct, and brief answer. If 'phone' field, give a phone number. If motivation or why or cover letter, give a short but strong pitch. If address/location, use 'Germany'."
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=60
                )
                return response['choices'][0]['message']['content'].strip()
            except Exception as e:
                print(f"⚠️ LLM failed: {e}")
