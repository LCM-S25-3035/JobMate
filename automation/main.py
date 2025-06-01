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
from os.path import isfile
import os

class EasyApplyLinkedin:
    def __init__(self, data):
        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        chrome_service = Service(data['driver_path'])
        self.driver = webdriver.Chrome(service=chrome_service)
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

    def submit_application(self, job_ad):
        print("🔍 Submitting application for:", job_ad.text)

        def extract_job_info():
            try: title = self.driver.find_element(By.CSS_SELECTOR, "h2.topcard__title").text.strip()
            except: title = job_ad.text.strip()
            try: company = self.driver.find_element(By.CSS_SELECTOR, "span.topcard__flavor").text.strip()
            except: company = "N/A"
            try: location = self.driver.find_element(By.CSS_SELECTOR, "span.topcard__flavor--bullet").text.strip()
            except: location = "N/A"
            try: job_url = self.driver.current_url
            except: job_url = "N/A"
            return title, company, location, job_url

        for attempt in range(2):
            discarded = False
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_ad)
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(job_ad)).click()
                time.sleep(random.uniform(2.5, 4.0))

                title, company, location, job_url = extract_job_info()

                if any(elem.is_displayed() for elem in self.driver.find_elements(
                    By.XPATH, "//span[contains(text(), 'applied') or contains(text(), 'application submitted')]")):
                    print("🛑 Job already applied. Skipping.")
                    self.failed_apps.append((title, company, location, job_url, "Already applied"))
                    return

                easy_apply_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'jobs-apply-button')]"))
                )
                easy_apply_button.click()
                time.sleep(random.uniform(2.5, 4.0))

                while True:
                    time.sleep(2)
                    page_before = hash(self.driver.page_source)

                    try:
                        submit_btn = self.driver.find_element(By.XPATH, "//button[@aria-label='Submit application']")
                        if submit_btn.is_displayed():
                            submit_btn.click()
                            print("✅ Application submitted.")
                            self.successful_apps.append((title, company, location, job_url))
                            os.makedirs("screenshots", exist_ok=True)
                            self.driver.save_screenshot(f"screenshots/success_{title[:30].replace(' ', '_')}.png")
                            self.close_modal_if_present()
                            return
                    except: pass

                    try:
                        review_btn = self.driver.find_element(By.XPATH, "//button[@aria-label='Review your application']")
                        if review_btn.is_displayed():
                            review_btn.click()
                            print("➡️ Clicked Review")
                            time.sleep(2)
                            page_after = hash(self.driver.page_source)
                            if page_after == page_before:
                                print("⚠️ Review did not change the page. Discarding.")
                                discarded = True
                                self.close_modal_if_present()
                                break
                            continue
                    except: pass

                    try:
                        next_btn = self.driver.find_element(By.XPATH, "//button[@aria-label='Continue to next step']")
                        if next_btn.is_displayed():
                            next_btn.click()
                            print("➡️ Clicked Next")
                            time.sleep(2)
                            page_after = hash(self.driver.page_source)
                            if page_after == page_before:
                                print("⚠️ Next did not change the page. Discarding.")
                                discarded = True
                                self.close_modal_if_present()
                                break
                            continue
                    except: pass

                    print("⚠️ No actionable buttons found. Discarding.")
                    discarded = True
                    self.close_modal_if_present()
                    break

                if discarded:
                    print("🛑 Discarded application. Skipping retry.")
                    break

            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                self.close_modal_if_present()
                if attempt == 1 or discarded:
                    title, company, location, job_url = extract_job_info()
                    self.failed_apps.append((title, company, location, job_url, str(e)))
                    os.makedirs("screenshots", exist_ok=True)
                    self.driver.save_screenshot(f"screenshots/fail_{title[:30].replace(' ', '_')}.png")
                    break

    def close_modal_if_present(self):
        for xpath, msg in [
            ("//button[contains(@class, 'artdeco-modal__dismiss')]", "✔️ Closed success modal (dismiss X)."),
            ("//button[text()='Done']", "✔️ Clicked 'Done' to close modal."),
            ("//button[@aria-label='Dismiss']", "✔️ Closed modal using aria-label 'Dismiss'."),
            ("//button[.//span[text()='Discard']]", "🗑️ Clicked Discard in confirmation modal.")
        ]:
            try:
                btn = self.driver.find_element(By.XPATH, xpath)
                if btn.is_displayed():
                    btn.click()
                    print(msg)
                    return
            except: pass
        print("⚠️ Modal could not be dismissed or discarded.")

    def close_browser(self):
        self.driver.quit()

