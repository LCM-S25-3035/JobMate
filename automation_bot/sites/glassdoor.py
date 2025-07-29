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
    def __init__(self, driver_path, profile_path, config=None):
        # Store config
        self.config = config or {}
        
        # Initialize modular components
        self.browser = BrowserManager(driver_path, profile_path)
        self.driver = self.browser.driver
        self.login = LoginHandler(self.driver, profile_path)
        self.scraper = FormScraper(self.driver, profile_path)
        self.navigation = NavigationManager(self.driver, self.browser)
        self.submitter = ApplicationSubmitter(self.driver, self.browser)
        self.filler = FormFiller(self.driver, self.navigation, self.submitter, self.config)
        self.captcha = CaptchaHandler(self.driver)
        
        # Track popup states to avoid redundant checks
        self.job_alert_popup_dismissed = False

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
            print("Checking if login is needed...")
            login_button_clicked = self.login.dynamic_login()
            
            if login_button_clicked:
                print("Login button was clicked. Proceeding with modal login flow...")
                # Add debug info before modal handling
                print("Debugging page state before modal handling...")
                self.debug_page_elements()
                
                if self.handle_modal_login():
                    print("Modal login completed.")
                else:
                    print("No modal detected after Sign In.")
            else:
                print("No login required. Already signed in. Skipping login flow.")
                
            # Buffer and popup check post-login
            print("Waiting for UI to settle...")
            time.sleep(1)
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

        # Give the modal time to appear
        time.sleep(1)  # Reduced from 2 to 1 second
        
        print("=== STEP 1: EMAIL MODAL ===")
        # Try to find email input first
        email_filled = False
        try:
            # Look for email input field specifically
            email_input = self.driver.find_element(By.XPATH, "//input[@type='email' or @data-test='emailInput-input']")
            if email_input.is_displayed():
                print("Found email input field")
                # Clear and fill email
                email_input.clear()
                for char in self.login.email:
                    email_input.send_keys(char)
                    time.sleep(0.1)
                print(f"Filled email: {self.login.email}")
                email_filled = True
            else:
                print("Email input not visible")
        except Exception as e:
            print(f"Could not find email input: {e}")

        # If email was filled, look for "Continue with email" button
        if email_filled:
            try:
                # Look for the specific "Continue with email" button
                continue_btn = self.driver.find_element(By.XPATH, 
                    "//button[@data-test='continue-with-email-modal' or contains(text(), 'Continue with email')]")
                
                if continue_btn.is_displayed() and continue_btn.is_enabled():
                    print("Found 'Continue with email' button")
                    self.browser.scroll_into_view(continue_btn)
                    continue_btn.click()
                    print("Clicked 'Continue with email' button")
                    time.sleep(2)  # Wait for password modal to appear
                else:
                    print("Continue with email button not clickable")
                    return False
            except Exception as e:
                print(f"Could not find/click Continue with email button: {e}")
                return False

        print("=== STEP 2: PASSWORD MODAL ===")
        # Now handle password modal
        password_filled = False
        try:
            # Wait for password modal to appear and look for password input
            print("Waiting for password modal to load...")
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='password' or @data-test='passwordInput-input']"))
            )
            
            # Additional wait to ensure field is ready for input
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(password_input)
            )
            
            if password_input.is_displayed():
                print("Found password input field")
                # Clear and fill password
                password_input.clear()
                time.sleep(0.5)  # Small delay after clearing
                
                for char in self.login.password:
                    password_input.send_keys(char)
                    time.sleep(0.1)
                print("Filled password field")
                
                # Give a moment for any validation to occur
                time.sleep(1)
                password_filled = True
            else:
                print("Password input not visible")
        except Exception as e:
            print(f"Could not find password input: {e}")

        # If password was filled, look for sign in button
        if password_filled:
            try:
                print("Waiting for Sign in button to become clickable...")
                # Wait a bit for any loading to complete
                time.sleep(1)
                
                # Try multiple selectors for the sign in button based on actual HTML structure
                signin_selectors = [
                    "//button[@type='submit' and @data-loading='false']//span[contains(text(), 'Sign in')]/..",
                    "//button[contains(@class, 'Button') and @type='submit' and @data-loading='false']",
                    "//div[@class='d-flex align-items-center flex-column emailButton']//button[@type='submit']",
                    "//button[@type='submit' and @data-role-variant='primary']//span[contains(text(), 'Sign in')]/..",
                    "//button[@type='submit' and contains(@class, 'Button')]",
                    "//button[@type='submit' and @data-loading='false']",
                    "//button[contains(text(), 'Sign in')]",
                    "//form//button[@type='submit']"
                ]
                
                signin_btn = None
                for selector in signin_selectors:
                    try:
                        # Wait for button to be present and clickable
                        signin_btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        if signin_btn.is_displayed():
                            print(f"Found Sign in button with selector: {selector}")
                            break
                    except Exception:
                        continue
                
                if signin_btn:
                    print(f"Found 'Sign in' button with selector: {selector}")
                    print(f"Button text: '{signin_btn.text}'")
                    print(f"Button class: '{signin_btn.get_attribute('class')}'")
                    print(f"Button type: '{signin_btn.get_attribute('type')}'")
                    print(f"Button data-loading: '{signin_btn.get_attribute('data-loading')}'")
                    
                    self.browser.scroll_into_view(signin_btn)
                    
                    # Check if button is still loading
                    loading_attr = signin_btn.get_attribute("data-loading")
                    if loading_attr == "true":
                        print("Button is loading, waiting...")
                        WebDriverWait(self.driver, 10).until(
                            lambda d: signin_btn.get_attribute("data-loading") != "true"
                        )
                        print("Button loading completed")
                    
                    # Try clicking the button with enhanced approach
                    try:
                        # First ensure the button is in view and ready
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", signin_btn)
                        time.sleep(0.5)
                        
                        # Try normal click first
                        signin_btn.click()
                        print("Clicked 'Sign in' button")
                    except Exception as click_err:
                        print(f"Normal click failed: {click_err}")
                        try:
                            # If normal click fails, try JavaScript click on the button
                            print("Trying JavaScript click on button...")
                            self.driver.execute_script("arguments[0].click();", signin_btn)
                            print("Clicked 'Sign in' button with JavaScript")
                        except Exception as js_err:
                            print(f"JavaScript click failed: {js_err}")
                            # Last resort: try clicking the span inside the button
                            try:
                                span_element = signin_btn.find_element(By.XPATH, ".//span[contains(text(), 'Sign in')]")
                                span_element.click()
                                print("Clicked 'Sign in' span element")
                            except Exception as span_err:
                                print(f"Span click also failed: {span_err}")
                                raise
                    
                    time.sleep(3)  # Wait for login to complete
                    return True
                else:
                    print("Could not find any clickable Sign in button")
                    # Debug: show all buttons on the page
                    all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    button_texts = [btn.text.strip() for btn in all_buttons if btn.is_displayed() and btn.text.strip()]
                    print(f"All visible buttons: {button_texts}")
                    
            except Exception as e:
                print(f"Could not find/click Sign in button: {e}")
                # Try one more fallback approach
                try:
                    print("Trying fallback: any submit button in form...")
                    submit_btn = self.driver.find_element(By.XPATH, "//form//button")
                    if submit_btn.is_displayed():
                        submit_btn.click()
                        print("Clicked fallback submit button")
                        time.sleep(3)
                        return True
                except Exception as fallback_err:
                    print(f"Fallback also failed: {fallback_err}")

        if email_filled or password_filled:
            return True  # Some progress was made
        else:
            print("No modal login fields found")
            return False

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
                time.sleep(0.05)  # Reduced from 0.1 to 0.05 seconds
            location_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "searchBar-location"))
            )
            location_input.clear()
            for char in location:
                location_input.send_keys(char)
                time.sleep(0.05)  # Reduced from 0.1 to 0.05 seconds
            location_input.send_keys(Keys.RETURN)
            print("Submitted search.")
            time.sleep(1)  # Reduced from 2 to 1 second

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
        except Exception:
            print("No 'Save job alert' popup detected.")

    def click_easy_apply_toggle(self):
        try:
            print("Looking for 'Easy Apply only' toggle button...")
            # Check for popups first (only if not already dismissed)
            self.handle_create_job_alert_popup()
            self.browser.handle_generic_popups()
            time.sleep(1)  # Reduced from 2 to 1 second

            easy_apply_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Easy Apply only') or @data-test='applicationType']"))
            )

            # Now scroll and then click easy apply filter
            self.browser.scroll_into_view(easy_apply_btn)
            time.sleep(0.5)

            self.browser.click_element(easy_apply_btn, site_modal_handler=self.handle_create_job_alert_popup)
            print("Clicked 'Easy Apply only' toggle button.")
            time.sleep(1)  # Reduced from 2 to 1 second

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
            max_jobs = self.config.get('max_jobs', 20)  # Default to 20 if not specified
            print(f"Found {len(job_cards)} Easy Apply job listings, applying to first {max_jobs}.")

            original_tab = self.driver.current_window_handle

            for index, card in enumerate(job_cards[:max_jobs], start=1):
                try:
                    # Check for popups first (only if not already dismissed)
                    self.handle_create_job_alert_popup()
                    self.browser.handle_generic_popups()

                    print(f"Job {index}: Clicking job card...")
                    self.browser.scroll_into_view(card)
                    time.sleep(0.3)  # Reduced from 0.5 to 0.3 seconds
                    self.browser.click_element(card)
                    time.sleep(1)  # Reduced from 2 to 1 second - Wait for side pane to load

                    # Locate Easy Apply button within the job details
                    print(f"Job {index}: Looking for Easy Apply button...")
                    easy_apply_btn = self.driver.find_elements(By.XPATH, "//button[@data-test='easyApply']")

                    if easy_apply_btn:
                        try:
                            print(f"Job {index}: Found Easy Apply button. Attempting to click...")
                            self.browser.scroll_into_view(easy_apply_btn[0])
                            self.browser.click_element(easy_apply_btn[0])
                            print(f"Job {index}: Clicked 'Easy Apply'.")
                        except Exception:
                            print(f"Job {index}: Click intercepted. Checking for blocking modals...")
                            self.handle_job_alert_popup()  # Different popup - keep this check
                            self.browser.handle_generic_popups()  # fallback
                            print("Retrying click after dismissing modal...")
                            self.browser.scroll_into_view(easy_apply_btn[0])
                            self.browser.click_element(easy_apply_btn[0])
                            print(f"Job {index}: Clicked 'Easy Apply' after dismissing modal.")

                        # Proceed with application flow
                        time.sleep(2)  # Reduced from 3 to 2 seconds
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
        Only checks if it hasn't been dismissed already.
        """
        if self.job_alert_popup_dismissed:
            return  # Skip if already dismissed
            
        try:
            print("Checking for 'Create Job Alert' popup...")
            popup = WebDriverWait(self.driver, 2).until(  # Reduced timeout from 5 to 2 seconds
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
                self.job_alert_popup_dismissed = True  # Mark as dismissed
                time.sleep(1)  # Give UI time to settle
            else:
                print("No close button found in 'Create Job Alert' popup.")
        except Exception:
            # No popup found - this is normal, don't print error
            print("No 'Create Job Alert' popup detected.")

    def smart_popup_check_after_return(self):
        """
        Check for popups only when returning from job applications to search results.
        This is when job alert popups typically appear.
        """
        if not self.job_alert_popup_dismissed:
            print("Checking for popups after returning to search results...")
            self.handle_create_job_alert_popup()
            self.browser.handle_generic_popups()
        else:
            print("Skipping popup check - already handled")

    def debug_page_elements(self):
        """Debug method to see what elements are currently on the page"""
        print("\n=== DEBUG: Current page elements ===")
        try:
            # Check for any modals, popups, or overlays
            all_divs = self.driver.find_elements(By.TAG_NAME, "div")
            modal_like_divs = []
            
            for div in all_divs:
                class_attr = div.get_attribute("class") or ""
                if any(keyword in class_attr.lower() for keyword in ["modal", "popup", "overlay", "dialog", "sign", "login", "auth"]):
                    if div.is_displayed():
                        modal_like_divs.append(f"Class: {class_attr}")
            
            print(f"Found {len(modal_like_divs)} modal-like divs:")
            for div_info in modal_like_divs[:5]:  # Show first 5
                print(f"  - {div_info}")
            
            # Check for forms
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            print(f"Found {len(forms)} forms on page")
            
            # Check for input fields
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            email_inputs = [inp for inp in inputs if inp.get_attribute("type") == "email" and inp.is_displayed()]
            password_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password" and inp.is_displayed()]
            
            print(f"Found {len(email_inputs)} visible email inputs")
            print(f"Found {len(password_inputs)} visible password inputs")
            
            # Check for buttons
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            visible_buttons = [btn.text.strip() for btn in buttons if btn.is_displayed() and btn.text.strip()]
            print(f"Visible buttons: {visible_buttons[:10]}")  # Show first 10
            
        except Exception as e:
            print(f"Debug failed: {e}")
        print("=== END DEBUG ===\n")

    def quit(self):
        self.browser.quit()
