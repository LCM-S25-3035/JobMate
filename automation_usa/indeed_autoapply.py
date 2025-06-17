import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def run_undetected_login(driver_path, profile_path, login_url):
    import undetected_chromedriver as uc
    os.makedirs(profile_path, exist_ok=True)

    print("Launching undetected Chrome for login...")
    driver = uc.Chrome(
        driver_executable_path=driver_path,
        user_data_dir=profile_path,
        headless=False
    )
    driver.get(login_url)
    print("Please log in manually. This session will be saved.")
    input("Press Enter when done...")
    driver.quit()


class IndeedSmartApplyInspector:
    def __init__(self, driver):
        self.driver = driver

    def extract_fields(self):
        inputs = self.driver.find_elements(By.XPATH, "//input | //textarea | //select")
        fields = []
        for field in inputs:
            label = (
                field.get_attribute("aria-label")
                or field.get_attribute("name")
                or field.get_attribute("placeholder")
            )
            if label:
                fields.append(label.strip())
        return fields

    def extract_buttons(self):
        buttons = self.driver.find_elements(By.XPATH, "//button")
        visible_buttons = []
        for btn in buttons:
            if btn.is_displayed():
                label = btn.text.strip() or btn.get_attribute("aria-label")
                if label:
                    visible_buttons.append(label)
        return visible_buttons


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

    def search_jobs(self, keyword, location=""):
        try:
            what_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "text-input-what"))
            )
            what_input.clear()
            what_input.send_keys(keyword)

            where_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "text-input-where"))
            )

            # This clears location input aggressively
            where_input.click()
            where_input.send_keys(Keys.CONTROL + "a")  # Select all
            where_input.send_keys(Keys.BACKSPACE)      # Delete

            if location:
                where_input.send_keys(location)

            where_input.send_keys(Keys.RETURN)
            print(f"Searched for: {keyword} in {location or 'default location'}")
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
                        time.sleep(2)

                        inspector = IndeedSmartApplyInspector(self.driver)
                        fields = inspector.extract_fields()
                        buttons = inspector.extract_buttons()

                        print("Detected Form Fields:")
                        for f in fields:
                            print(" -", f)
                        print("Detected Buttons:")
                        for b in buttons:
                            print(" -", b)

                        input("Press Enter after applying (or to skip)...")
                    else:
                        print("No Apply Now button found.")
                except Exception as job_e:
                    print(f"Error applying to job {i + 1}: {job_e}")
        except Exception as e:
            print("Failed to locate job cards:", e)

    def quit(self):
        input("Press Enter to close browser...")
        self.driver.quit()


if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

    if config.get("login_only", False):
        run_undetected_login(
            config["driver_path"],
            config["profile_path"],
            config["indeed_url"]
        )
        exit()

    bot = IndeedBot(
        driver_path=config["driver_path"],
        profile_path=config["profile_path"]
    )

    bot.open_homepage(config["indeed_url"])
    bot.search_jobs(keyword=config["keyword"], location=config.get("location", ""))
    bot.apply_to_all_easy_apply_jobs()
    bot.quit()

# Reference
# OpenAI, 4o 1st prompt: "actually then might as well just do for indeed? now that i can bypass the cloudflare?"
# OpenAI, 4o last prompt: ""Toronto, ONLondonLondon this is what's happening. i want to remove all fields""