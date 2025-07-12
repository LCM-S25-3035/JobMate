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

    def paginate_and_apply(self):
        """Paginates through job listings and applies to each one."""
        base_url = self.driver.current_url.split('&start=')[0]
        total_results = self.get_total_results()
        total_pages = (total_results // 25) + 1
        print(f"Total pages to process: {total_pages}")

        for page_num in range(total_pages):
            start = page_num * 25
            paginated_url = f"{base_url}&start={start}"
            self.driver.get(paginated_url)
            print(f"📄 Navigated to page {page_num + 1}/{total_pages}")
            
            print("Pausing to prevent bot detection...")
            time.sleep(random.uniform(5, 10)) 
            
            job_cards = self.extract_job_cards()

            for job in job_cards:
                self.submit_application(job)
                time.sleep(random.uniform(2, 5))

    def submit_application(self, job_ad):
        """Handles the application process for a single job, skipping external 'Apply' links."""
        print("="*50)
        
        try: 
            title = job_ad.find_element(By.CSS_SELECTOR, 'a.job-card-list__title').text.strip()
            print(f"🔍 Processing application for: {title}")
        except NoSuchElementException:
            title = job_ad.text.splitlines()[0]
            print(f"🔍 Processing application for: {title} (fallback)")

        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_ad)
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(job_ad)).click()
            
            # We no longer fetch company name here to simplify the process.
            # We only need the URL for logging.
            time.sleep(1) # Short pause for the URL to update
            job_url = self.driver.current_url

            if any(elem.is_displayed() for elem in self.driver.find_elements(
                    By.XPATH, "//span[contains(text(), 'Applied') or contains(text(), 'Application submitted')]")):
                print("🛑 Job already applied. Skipping.")
                # Note: "company" and "location" are placeholders now
                self.failed_apps.append((title, "N/A", "N/A", job_url, "Already applied"))
                return

            try:
                apply_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'jobs-apply-button')]")
                apply_button_text = apply_button.text.strip()
                if "easy" not in apply_button_text.lower():
                    print("⚠️ Detected external ‘Apply’ button. Skipping job.")
                    self.failed_apps.append((title, "N/A", "N/A", job_url, "External Apply Button"))
                    return
            except NoSuchElementException:
                print("❌ Could not find apply button. Skipping job.")
                self.failed_apps.append((title, "N/A", "N/A", job_url, "Apply button not found"))
                return

            apply_button.click()
            time.sleep(random.uniform(2.5, 4.0))

            while True:
                time.sleep(2)
                page_before = hash(self.driver.page_source)

                try:
                    submit_btn = self.driver.find_element(By.XPATH, "//button[@aria-label='Submit application']")
                    if submit_btn.is_displayed():
                        submit_btn.click()
                        print("✅ Application submitted successfully.")
                        # Note: "company" and "location" are placeholders now
                        self.successful_apps.append((title, "N/A", "N/A", job_url))
                        
                        print("    - Pausing for 3 seconds...")
                        time.sleep(3)
                        
                        self.close_modal_if_present()
                        return
                        
                except: pass

                try:
                    review_btn = self.driver.find_element(By.XPATH, "//button[@aria-label='Review your application']")
                    if review_btn.is_displayed():
                        review_btn.click()
                        print("➡️ Clicked Review")
                        time.sleep(2)
                        if hash(self.driver.page_source) == page_before:
                            print("⚠️ Review did not change the page. Discarding.")
                            self.close_modal_if_present(discard=True)
                            self.failed_apps.append((title, "N/A", "N/A", job_url, "Stuck on Review"))
                            return
                        continue
                except: pass

                try:
                    next_btn = self.driver.find_element(By.XPATH, "//button[@aria-label='Continue to next step']")
                    if next_btn.is_displayed():
                        next_btn.click()
                        print("➡️ Clicked Next")
                        time.sleep(2)
                        if hash(self.driver.page_source) == page_before:
                            print("⚠️ Next did not change the page. Discarding.")
                            self.close_modal_if_present(discard=True)
                            self.failed_apps.append((title, "N/A", "N/A", job_url, "Stuck on Next"))
                            return
                        continue
                except: pass

                print("⚠️ No actionable buttons found. Discarding.")
                self.close_modal_if_present(discard=True)
                self.failed_apps.append((title, "N/A", "N/A", job_url, "No actionable buttons"))
                return

        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
            self.failed_apps.append((title, "N/A", "N/A", self.driver.current_url, str(e)))
            self.close_modal_if_present(discard=True)


    def close_modal_if_present(self, discard=False):
        """Closes or discards the application modal."""
        try:
            close_button = self.driver.find_element(By.XPATH, "//button[contains(@class, 'artdeco-modal__dismiss')]")
            close_button.click()
            print("-> Clicked modal close button 'X'.")
            time.sleep(1.5)
            if discard:
                try:
                    discard_button = self.driver.find_element(By.XPATH, "//button[.//span[text()='Discard']]")
                    discard_button.click()
                    print("🗑️ Confirmed Discard.")
                except NoSuchElementException:
                    print("- No discard confirmation pop-up found, assuming modal is closed.")
            return
        except (NoSuchElementException, TimeoutException):
            pass

        try:
            done_button = self.driver.find_element(By.XPATH, "//button[text()='Done']")
            done_button.click()
            print("✔️ Clicked 'Done'.")
        except (NoSuchElementException, TimeoutException):
            print("- No 'Done' button found.")
            pass


    def close_browser(self):
        """Closes the browser."""
        try:
            self.driver.quit()
        except Exception as e:
            print(f"Browser already closed or an error occurred during quit: {e}")

def write_log_file(bot):
    """Writes the results of the bot's run to a CSV file."""
    print("\n" + "="*50)
    print("Writing log file...")
    print(f"Successful applications: {len(bot.successful_apps)}")
    print(f"Failed/Skipped applications: {len(bot.failed_apps)}")
    print("="*50)
    
    filename = "successful_applications_log.csv"
    log_exists = isfile(filename)
    
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            # --- HEADERS AND ROW CORRECTED TO REMOVE COMPANY ---
            headers = ['Date', 'Job Title', 'Job URL']
            writer = csv.writer(f)
            
            if not log_exists:
                writer.writerow(headers)
            
            # The loop still unpacks 'company' and 'location' but they are ignored
            for title, company, location, url in bot.successful_apps:
                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), title, url])
            # --- END OF CHANGE ---
        print(f"✓ Log successfully written to {filename}")
    except Exception as e:
        print(f"⚠️ Could not write log file: {e}")


if __name__ == "__main__":
    with open('config.json') as config_file:
        data = json.load(config_file)

    bot = EasyApplyLinkedin(data)
    
    try:
        bot.login_linkedin()
        bot.job_search()
        bot.filter()
        bot.paginate_and_apply()
    except Exception as e:
        print(f"\n--- An unexpected error occurred in the main process: {e} ---")
    finally:
        print("\n--- Script ending. Writing logs and closing browser. ---")
        write_log_file(bot)
        bot.close_browser()
###last working version
