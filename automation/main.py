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

        # ✅ ADDED: Track results
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
        self.driver.maximize_window()
        time.sleep(30)
        self.driver.get("https://www.linkedin.com/jobs/")

    def job_search(self):  # To put in the job name and location in the search bar then enter
        wait = WebDriverWait(self.driver, 15)
        search_keyword = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[starts-with(@id,'jobs-search-box-keyword')]"))
        )
        search_keyword.clear()
        search_keyword.send_keys(self.keywords)
        time.sleep(3)

        search_location = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[starts-with(@id,'jobs-search-box-location')]"))
        )
        search_location.clear()
        search_location.send_keys(self.location)
        time.sleep(3)
        search_location.send_keys(Keys.RETURN)

    def filter(self):
        try:  # Clicking the easy apply button to bar filter
            easy_apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "searchFilter_applyWithLinkedin"))
            )
            easy_apply_button.click()
            time.sleep(2)
        except Exception as e:
            print("❌ Easy Apply top bar filter not found or not clickable:", e)
        time.sleep(2)

    def find_offers(self):
        self.job_cards = []  # ✅ ADDED
        page = 1
        while True:
            print(f"📄 Scraping page {page}...")

            try:
                results_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'jobs-search-results-list__subtitle')]//span"))
                )
                results_text = results_element.text
                total_results = int(results_text.split()[0].replace(",", ""))
                print("🔎 Total job results found:", total_results)
            except Exception as e:
                print("❌ Could not fetch total results count:", e)
            time.sleep(2)

            try:
                cards = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_all_elements_located((
                        By.CSS_SELECTOR,
                        "div.job-card-container.relative.job-card-list.job-card-container--clickable"
                    ))
                )
                for result in cards:
                    hover = ActionChains(self.driver).move_to_element(result)
                    hover.perform()
                    time.sleep(random.uniform(1.5, 3.0))  # ✅ ADDED
                    self.job_cards.append(result)
            except Exception as e:
                print("❌ Could not find job cards:", e)

            try:
                next_btn = self.driver.find_element(By.XPATH, "//button[@aria-label='Next']")
                if "disabled" in next_btn.get_attribute("class"):
                    print("✅ No more pages.")
                    break
                else:
                    next_btn.click()
                    page += 1
                    time.sleep(random.uniform(3.5, 6.0))  # ✅ ADDED
            except:
                print("🚫 Next button not found. Exiting.")
                break

    def submit_application(self, job_ad):
        print("🔍 Submitting application for:", job_ad.text)

        for attempt in range(2):  # ✅ ADDED: Retry logic
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_ad)
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(job_ad))
                self.driver.execute_script("arguments[0].click();", job_ad)
                time.sleep(random.uniform(2.5, 4.0))

                easy_apply_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'jobs-apply-button')]"))
                )
                easy_apply_button.click()
                time.sleep(random.uniform(2.5, 4.0))

                while True:
                    time.sleep(2)
                    try:
                        submit_btn = self.driver.find_element(By.XPATH, "//button[@aria-label='Submit application']")
                        submit_btn.click()
                        print("✅ Application submitted.")

                        filename = job_ad.text.replace(" ", "_")[:40] + "_submitted.png"
                        self.driver.save_screenshot(filename)
                        print(f"🖼️ Screenshot saved: {filename}")

                        try:
                            close_btn = self.driver.find_element(By.XPATH, "//button[@aria-label='Dismiss']")
                            close_btn.click()
                            print("❎ Closed application modal.")
                        except:
                            print("⚠️ Could not close modal.")
                        self.successful_apps.append(job_ad.text)
                        return
                    except:
                        pass

                    try:
                        self.driver.find_element(By.XPATH, "//button[@aria-label='Review your application']").click()
                        print("➡️ Clicked Review")
                        continue
                    except:
                        pass

                    try:
                        self.driver.find_element(By.XPATH, "//button[@aria-label='Continue to next step']").click()
                        print("➡️ Clicked Next")
                        continue
                    except:
                        pass

                    print("⚠️ No further buttons found.")
                    break

                try:
                    self.driver.find_element(By.XPATH, "//span[contains(text(), 'applied')]")
                    print("🛑 Already applied.")
                    return
                except:
                    pass

                break  # ✅ Exit retry loop on success
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt == 1:
                    self.failed_apps.append((job_ad.text, str(e)))

    def close_browser(self):
        self.driver.quit()


# ✅ ADDED: Auto-restart main logic
if __name__ == "__main__":
    MAX_RETRIES = 3  # Max restart attempts
    attempt = 0

    while attempt < MAX_RETRIES:
        try:
            with open('config.json') as config_file:
                data = json.load(config_file)

            bot = EasyApplyLinkedin(data)
            bot.login_linkedin()
            bot.job_search()
            bot.filter()
            bot.find_offers()

            for job in bot.job_cards:
                time.sleep(random.uniform(4.0, 7.0))  # ✅ Human-like delay
                bot.submit_application(job)

            break  # ✅ Success: Exit retry loop

        except Exception as e:
            attempt += 1
            print(f"🔁 Attempt {attempt} failed: {e}")
            if attempt >= MAX_RETRIES:
                print("❌ Max retries reached. Exiting.")
                break
            print("⏳ Restarting after 10 seconds...")
            time.sleep(10)

        finally:
            try:
                bot.close_browser()
            except:
                pass

            # ✅ Always log results even on failure
            with open('job_application_log.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Status', 'Job Title', 'Error Message', 'Timestamp'])

                for job in bot.successful_apps:
                    writer.writerow(['Success', job, '', datetime.now().isoformat()])
                for job, error in bot.failed_apps:
                    writer.writerow(['Failed', job, error, datetime.now().isoformat()])
