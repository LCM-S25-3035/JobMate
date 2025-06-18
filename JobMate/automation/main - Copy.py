from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import json
import time

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

    def job_search(self):
        '''Going to put in job name and location in the search bar then enter'''
        wait = WebDriverWait(self.driver, 15)
        search_keyword = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[starts-with(@id,'jobs-search-box-keyword')]")
            )
        )

        search_keyword.clear()
        search_keyword.send_keys(self.keywords)
        time.sleep(2)

        # Wait and input location
        search_location = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[starts-with(@id,'jobs-search-box-location')]")
            )
        )
        search_location.clear()
        search_location.send_keys(self.location)
        time.sleep(2)
        search_location.send_keys(Keys.RETURN)


    def close_browser(self):
        """Properly quit the browser"""
        self.driver.quit()

if __name__ == "__main__":
    with open('config.json') as config_file:
        data = json.load(config_file)
    bot = EasyApplyLinkedin(data)
    bot.login_linkedin()  # Log in and go to Jobs page
    bot.job_search()      # Search for the job title and location
    try:
        for _ in range(300):
            time.sleep(1)
            bot.driver.current_url  # Throw an exception if the browser is closed manually
    except Exception:
        pass
    finally:
        bot.close_browser()
