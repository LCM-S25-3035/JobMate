import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.browser_manager import BrowserManager
from core.login_handler import LoginHandler
from core.form_scraper import FormScraper
from core.form_filler import FormFiller
from core.navigation_manager import NavigationManager
from core.submit_handler import ApplicationSubmitter
from core.captcha_handler import CaptchaHandler

class GlassdoorBot:
    def __init__(self, driver_path, profile_path):
        # Initialize modular components
        self.browser = BrowserManager(driver_path, profile_path)
        self.driver = self.browser.driver
        self.login = LoginHandler(self.driver, profile_path)
        self.scraper = FormScraper(self.driver, profile_path)
        self.navigation = NavigationManager(self.driver, self.browser)
        self.submitter = ApplicationSubmitter(self.driver, self.browser)
        self.filler = FormFiller(self.driver, self.navigation, self.submitter)
        self.captcha = CaptchaHandler(self.driver)

    def run(self):
        try:
            print("Starting Glassdoor automation...")

            # Load Glassdoor URL
            glassdoor_url = os.getenv("GLASSDOOR_URL")
            if not glassdoor_url:
                raise ValueError("GLASSDOOR_URL not set in environment variables.")

            print(f"Opening homepage: {glassdoor_url}")
            self.browser.driver.get(glassdoor_url)
            time.sleep(3)  # Let the homepage load

            # Dismiss cookies
            self.dismiss_cookie_popup()

            # Login flow
            print("Trying to click login button based on scraped buttons...")
            self.login.dynamic_login()
            print("Success! Dynamic login button clicked.")
            if self.handle_modal_login():
                print("Modal login completed.")
            else:
                print("No modal detected after Sign In. Assuming logged in.")

            # Buffer and popup check post-login
            print("Waiting for UI to settle post-login...")
            time.sleep(2)
            self.handle_create_job_alert_popup()
            self.handle_job_alert_popup()
            self.browser.handle_generic_popups()

            # Search and filter jobs
            self.search_jobs()

            # Click Easy Apply toggle
            self.click_easy_apply_toggle()

            # Loop through Easy Apply jobs
            self.click_easy_apply_jobs()

        except Exception as e:
            print(f"Glassdoor automation failed: {e}")
        finally:
            self.browser.quit()

    def dismiss_cookie_popup(self):
        try:
            print("Checking for cookie consent popup...")
            self.browser.handle_generic_popups()  # Moved to BrowserManager
        except:
            print("No cookie popup detected or it did not load in time.")

    def handle_modal_login(self):
        """
        Handle modal login flow if modal is detected.
        Returns True if modal was handled, False otherwise.
        """
        self.dismiss_cookie_popup()

        modal_data = self.scraper.scrape_modal_contents()
        if modal_data.get("buttons") or modal_data.get("inputs"):
            print("Modal detected. Processing modal inputs...")
            # Fill email
            if any(inp.get("type") == "email" for inp in modal_data.get("inputs", [])):
                self.login.fill_email_field()
                if self.browser.find_and_click_dynamic_button("Continue with email"):
                    time.sleep(1)
                    modal_data = self.scraper.scrape_modal_contents()

            # Fill password
            if any(inp.get("type") == "password" for inp in modal_data.get("inputs", [])):
                self.login.fill_password_field()
                if self.browser.find_and_click_dynamic_button("Sign in"):
                    print("Clicked 'Sign in' button in modal.")
                else:
                    print("Could not find 'Sign in' button.")
            return True  # Modal login handled
        else:
            print("No modal detected.")
            return False  # No modal, return control to login()

    def search_jobs(self):
        keyword = os.getenv("KEYWORD")
        location = os.getenv("LOCATION")
        print(f"Searching for '{keyword}' in '{location}' on Glassdoor...")
        try:
            keyword_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "searchBar-jobTitle"))
            )
            keyword_input.clear()
            for char in keyword:
                keyword_input.send_keys(char)
                time.sleep(0.1)
            location_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "searchBar-location"))
            )
            location_input.clear()
            for char in location:
                location_input.send_keys(char)
                time.sleep(0.1)
            location_input.send_keys(Keys.RETURN)
            print("Submitted search.")
            time.sleep(2)

            # Check for popups immediately after search
            print("Checking for popups after search...")
            self.handle_create_job_alert_popup()
            self.browser.handle_generic_popups()

        except Exception as e:
            print(f"Error during Glassdoor search: {e}")

    def handle_job_alert_popup(self):
        try:
            print("Checking for 'Save job alert' popup...")
            popup = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'modal')]")
            ))
            no_thanks_btn = popup.find_element(By.XPATH, ".//button[contains(text(), 'No thanks')]")
            if no_thanks_btn:
                self.browser.click_element(no_thanks_btn)
                print("Dismissed 'Save job alert' popup.")
                time.sleep(1)
        except:
            print("No 'Save job alert' popup detected.")

    def click_easy_apply_toggle(self):
        try:
            print("Looking for 'Easy Apply only' toggle button...")
            # Check for popups first
            self.handle_create_job_alert_popup()
            self.browser.handle_generic_popups()
            time.sleep(2)

            easy_apply_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Easy Apply only') or @data-test='applicationType']"))
            )
            # Check for modals again before clicking
            self.handle_create_job_alert_popup()
            self.browser.handle_generic_popups()

            # Now scroll and then click easy apply filter
            self.browser.scroll_into_view(easy_apply_btn)
            time.sleep(0.5)

            self.browser.click_element(easy_apply_btn, site_modal_handler=self.handle_create_job_alert_popup)
            print("Clicked 'Easy Apply only' toggle button.")
            time.sleep(2)

        except Exception as e:
            print(f"Could not find or click 'Easy Apply only' toggle: {e}")

    def click_easy_apply_jobs(self):
        """
        Loop through all job listings and apply to each one directly,
        assuming 'Easy Apply only' filter is active.
        """
        try:
            print("Getting filtered job listings...")
            job_cards = self.driver.find_elements(
                By.XPATH, "//li[@data-test='jobListing']"
            )
            print(f"Found {len(job_cards)} Easy Apply job listings.")

            original_tab = self.driver.current_window_handle

            for index, card in enumerate(job_cards[:30], start=1):
                try:
                    # Check for popups first
                    self.handle_create_job_alert_popup()
                    self.browser.handle_generic_popups()

                    print(f"Job {index}: Clicking job card...")
                    self.browser.scroll_into_view(card)
                    time.sleep(0.5)
                    self.browser.click_element(card)
                    time.sleep(2)  # Wait for side pane to load

                    # Locate Easy Apply button within the job details
                    print(f"Job {index}: Looking for Easy Apply button...")
                    easy_apply_btn = self.driver.find_elements(By.XPATH, "//button[@data-test='easyApply']")

                    if easy_apply_btn:
                        try:
                            print(f"Job {index}: Found Easy Apply button. Attempting to click...")
                            self.browser.scroll_into_view(easy_apply_btn[0])
                            self.browser.click_element(easy_apply_btn[0])
                            print(f"Job {index}: Clicked 'Easy Apply'.")
                        except Exception as click_err:
                            print(f"Job {index}: Click intercepted. Checking for blocking modals...")
                            self.handle_job_alert_popup()  # 🔥 Glassdoor-specific
                            self.browser.handle_generic_popups()  # fallback
                            print("Retrying click after dismissing modal...")
                            self.browser.scroll_into_view(easy_apply_btn[0])
                            self.browser.click_element(easy_apply_btn[0])
                            print(f"Job {index}: Clicked 'Easy Apply' after dismissing modal.")

                        # Proceed with application flow
                        time.sleep(3)
                        if self.navigation.switch_to_new_tab():
                            inputs_data = self.scraper.scrape_new_tab_inputs()
                            self.filler.fill_inputs_from_config_and_continue(inputs_data)

                            # reCAPTCHA check
                            self.captcha._wait_for_captcha()

                            # Submit application
                            self.submitter.submit_application_review()

                            # Switch back
                            self.navigation._switch_back_to_main_tab()

                    else:
                        print(f"Job {index}: No Easy Apply button found. Skipping this job.")

                except Exception as job_err:
                    print(f"Job {index}: Error during application: {job_err}")
                    # Attempt to switch back to original tab if possible
                    remaining_tabs = self.driver.window_handles
                    if original_tab in remaining_tabs:
                        self.driver.switch_to.window(original_tab)
                    continue

        except Exception as e:
            print(f"Error while processing Easy Apply jobs: {e}")

    def handle_create_job_alert_popup(self):
        """
        Detect and dismiss Glassdoor's 'Create Job Alert' popup modal.
        """
        try:
            print("Checking for 'Create Job Alert' popup...")
            popup = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "modal_ModalContainer__29cNw"))
            )
            # Look for close buttons
            close_btns = popup.find_elements(By.XPATH, """
                .//button[
                    contains(@aria-label, 'Close') or 
                    contains(@aria-label, 'Cancel') or 
                    contains(@class, 'modal_CloseButton') or 
                    contains(@data-test, 'job-alert-modal-close')
                ]
            """)
            if close_btns:
                print("Found 'Create Job Alert' popup. Dismissing it...")
                self.browser.scroll_into_view(close_btns[0])
                self.browser.click_element(close_btns[0])
                print("'Create Job Alert' popup dismissed.")
                time.sleep(1)  # Give UI time to settle
            else:
                print("No close button found in 'Create Job Alert' popup.")
        except Exception:
            print("No 'Create Job Alert' popup detected.")

    def quit(self):
        self.browser.quit()
