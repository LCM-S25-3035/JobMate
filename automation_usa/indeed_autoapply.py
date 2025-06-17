from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import json

class IndeedBot:
    def __init__(self, driver_path, profile_path):
        self.driver_path = driver_path
        self.profile_path = profile_path
        self.driver = self._launch_browser()

    def _launch_browser(self):
        os.makedirs(self.profile_path, exist_ok=True)

        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument(f"user-data-dir={self.profile_path}")

        return webdriver.Chrome(service=Service(self.driver_path), options=options)

    def open_homepage(self, url):
        print(f"Opening homepage: {url}")
        self.driver.get(url)
        time.sleep(3)

    def search_jobs(self, keyword="data analyst", location="London"):
        try:
            what_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "text-input-what"))
            )
            where_input = self.driver.find_element(By.ID, "text-input-where")

            what_input.clear()
            what_input.send_keys(keyword)

            where_input.clear()
            where_input.send_keys(location)
            where_input.send_keys(Keys.RETURN)

            print(f"Searched for '{keyword}' in '{location}'")
            time.sleep(3)
        except Exception as e:
            print("Search failed:", e)

    def apply_to_all_easy_apply_jobs(self):
        try:
            job_cards = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "job_seen_beacon"))
            )
            print(f"Found {len(job_cards)} job cards.")

            for i, card in enumerate(job_cards):
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView();", card)
                    time.sleep(1)
                    card.click()
                    print(f"Clicked job {i + 1}")
                    time.sleep(3)

                    apply_btns = self.driver.find_elements(By.CLASS_NAME, "ia-IndeedApplyButton")
                    if apply_btns:
                        apply_btns[0].click()
                        print("Clicked Apply Now.")

                        input("Press Enter after applying (or to skip)...")
                        print("Returned to job list.")
                    else:
                        print("No Apply Now button found.")
                except Exception as job_e:
                    print(f"Error applying to job {i + 1}: {job_e}")
        except Exception as e:
            print("Failed to locate job cards:", e)

    def quit(self):
        input("Press Enter to quit the browser...")
        self.driver.quit()

if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

    bot = IndeedBot(
        driver_path=config["driver_path"],
        profile_path=config["profile_path"]
    )

    bot.open_homepage(url=config["indeed_url"])
    bot.search_jobs(keyword=config["keyword"], location=config["location"])
    bot.apply_to_all_easy_apply_jobs()
    bot.quit()
