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

class GlassdoorBot:
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

    def login_with_google(self, email):
        try:
            google_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-test="googleBtn"]'))
            )
            google_button.click()

            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_field.send_keys(email)
            email_field.send_keys(Keys.RETURN)
            print("Google login step completed.")
        except Exception as e:
            print("Login failed or skipped:", e)

    def search_jobs(self, keyword="data analyst", location="London"):
        try:
            job_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchBar-jobTitle"))
            )
            loc_input = self.driver.find_element(By.ID, "searchBar-location")

            job_input.clear()
            job_input.send_keys(keyword)

            loc_input.clear()
            loc_input.send_keys(location)
            loc_input.send_keys(Keys.RETURN)

            print(f"Searched for '{keyword}' in '{location}'")
            time.sleep(3)
        except Exception as e:
            print("Search failed:", e)

    def dismiss_save_alert(self):
        try:
            buttons = self.driver.find_elements(By.XPATH, "//button[@data-test='job-alert-modal-cta-save']")
            if buttons:
                buttons[0].click()
                print("'Save this alert' modal dismissed.")
            else:
                print("No 'Save this alert' modal found.")
        except Exception as e:
            print("Error dismissing alert:", e)

    def filter_easy_apply(self):
        try:
            btn = self.driver.find_element(By.XPATH, "//button[@data-test='applicationType']")
            if btn.get_attribute("aria-pressed") == "false":
                btn.click()
                print("'Easy Apply only' filter toggled on.")
            else:
                print("'Easy Apply only' is already active.")
        except Exception as e:
            print("Failed to toggle Easy Apply filter:", e)

    def apply_to_all_easy_apply_jobs(self):
        try:
            job_cards = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//ul[contains(@class,'JobsList_jobs')]//li"))
            )
            print(f"Found {len(job_cards)} job cards.")

            for i, card in enumerate(job_cards):
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView();", card)
                    time.sleep(1)
                    card.click()
                    print(f"Clicked job {i + 1}")

                    time.sleep(3)
                    apply_btns = self.driver.find_elements(By.XPATH, "//button[@data-test='easyApply']")
                    if apply_btns:
                        main_window = self.driver.current_window_handle
                        apply_btns[0].click()
                        print("Clicked Easy Apply button.")
                        time.sleep(2)

                        WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
                        new_tabs = [tab for tab in self.driver.window_handles if tab != main_window]
                        if new_tabs:
                            self.driver.switch_to.window(new_tabs[0])
                            print("Switched to Easy Apply tab.")
                            time.sleep(3)
                            
                            if "indeed.com" in self.driver.current_url:
                                print("Indeed SmartApply opened — proceed with manual or automated apply.")
                                input("Press Enter after applying (or to skip)...")
                                self.driver.close()
                                self.driver.switch_to.window(main_window)
                                print("Returned to main job list.")
                                continue


                            self.driver.close()
                            print("Closed Easy Apply tab.")
                            self.driver.switch_to.window(main_window)
                            print("Returned to main job list.")
                    else:
                        print("No Easy Apply button found.")
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

    bot = GlassdoorBot(
        driver_path=config["driver_path"],
        profile_path=config["profile_path"]
    )

    bot.open_homepage(url=config["glassdoor_url"])
    bot.login_with_google(config["email"])
    bot.search_jobs(keyword=config["keyword"], location=config["location"])
    bot.dismiss_save_alert()
    bot.filter_easy_apply()
    bot.apply_to_all_easy_apply_jobs()
    bot.quit()
