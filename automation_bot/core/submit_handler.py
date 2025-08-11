import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ApplicationSubmitter:
    def __init__(self, driver, browser_manager):
        self.driver = driver
        self.browser_manager = browser_manager

    def upload_resume_smartapply(self):
        """
        If resume already exists, click it to activate and then click 'Continue'.
        """
        try:
            print("Checking for existing uploaded resume...")
            # Locate existing resume cards
            resume_cards = self.driver.find_elements(By.XPATH, "//div[contains(@data-testid, 'resume-card')]")
            if resume_cards:
                print(f"Found {len(resume_cards)} uploaded resume(s). Clicking the first one...")
                self.browser_manager.scroll_into_view(resume_cards[0])
                resume_cards[0].click()
                time.sleep(1)
            else:
                print("No uploaded resumes found. Waiting for manual upload...")
                input("Upload your resume manually and press Enter to continue...")

            # Click Continue button
            print("Looking for 'Continue' button after selecting resume...")
            continue_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'continue')]")
                )
            )
            self.browser_manager.scroll_into_view(continue_button)
            time.sleep(0.5)
            self.browser_manager.click_element(continue_button)
            print("Clicked 'Continue' button after selecting resume.")

        except Exception as e:
            from selenium.common.exceptions import NoSuchWindowException, WebDriverException
            if isinstance(e, (NoSuchWindowException, WebDriverException)):
                print("[Info] Window closed or not found during resume page actions.")
            else:
                print(f"Error on resume page: {e}")

    def submit_application_review(self):
        """
        Scrolls to the bottom of the review page, simulates human-like behavior,
        and clicks 'Submit your application'.
        """
        try:
            print("Checking if we are on the review page...")
            current_url = self.driver.current_url
            if "smartapply.indeed.com/beta/indeedapply/form/review" not in current_url:
                print(f"Not on review page. Current URL: {current_url}")
                return

            print("On review page. Preparing to submit application...")

            # Simulate human-like scrolling and pauses
            self.simulate_human_behavior()

            # Check for reCAPTCHA iframe
            if self.check_for_recaptcha():
                input("reCAPTCHA detected! Solve it manually in browser and press Enter...")

            # Retry clicking the Submit button
            clicked = False
            for attempt in range(1, 4):
                print(f"Attempt {attempt} to click 'Submit your application'...")
                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    submit_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit your application')]")
                        )
                    )
                    self.browser_manager.scroll_into_view(submit_button)
                    self.browser_manager.click_element(submit_button)
                    print("Successfully clicked 'Submit your application'.")
                    clicked = True
                    break
                except Exception as e:
                    print(f"Attempt {attempt} failed: {e}")
                    time.sleep(1)

            if not clicked:
                print("Failed to click Submit after retries.")
                input("Please manually click Submit in browser and press Enter to continue...")

            # After submit click, try to close tab
            self.handle_post_apply_and_close_tab()

            # Switch back to job listings tab
            self._switch_back_to_main_tab()

        except Exception as e:
            from selenium.common.exceptions import NoSuchWindowException, WebDriverException
            if isinstance(e, (NoSuchWindowException, WebDriverException)):
                print("[Info] Window closed or not found during application submission.")
            else:
                print(f"Error during application submission: {e}")

    def simulate_human_behavior(self):
        """
        Simulate human-like scrolling, hovering and random pauses.
        """
        import random
        from selenium.webdriver.common.action_chains import ActionChains

        print("Simulating human-like behavior on review page...")
        page_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_steps = random.randint(5, 10)
        for step in range(scroll_steps):
            scroll_position = (step / scroll_steps) * page_height
            self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(random.uniform(0.3, 0.8))

        # Hover over random buttons
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        if buttons:
            random_button = random.choice(buttons)
            print(f"Hovering over a random button: {random_button.text}")
            ActionChains(self.driver).move_to_element(random_button).perform()
            time.sleep(random.uniform(1, 2))

        # Random pause before clicking Submit
        delay = random.uniform(2, 5)
        print(f"Pausing {delay:.2f}s before clicking Submit...")
        time.sleep(delay)

    def check_for_recaptcha(self):
        """
        Checks for actual reCAPTCHA iframe and skips false positives.
        """
        print("Checking for reCAPTCHA on the page...")
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute("src")
                if src and "recaptcha" in src.lower():
                    if iframe.is_displayed():
                        print("Active reCAPTCHA detected!")
                        return True
            print("No visible reCAPTCHA found.")
            return False
        except Exception as e:
            from selenium.common.exceptions import NoSuchWindowException, WebDriverException
            if isinstance(e, (NoSuchWindowException, WebDriverException)):
                print("[Info] Window closed or not found during reCAPTCHA check.")
            else:
                print(f"Error during reCAPTCHA check: {e}")
            return False

    def _close_post_apply_tab_if_needed(self):
        """
        Closes the current tab if redirected to a POST_APPLY page (Indeed or Glassdoor).
        """
        current_url = self.driver.current_url.lower()
        if "post-apply" in current_url or "smart-apply-action=post_apply" in current_url:
            print(f"Detected POST_APPLY redirect at {current_url}. Closing this tab...")
            self.driver.close()
            time.sleep(1)
            return True
        return False

    def handle_post_apply_and_close_tab(self):
        """
        Wait for POST_APPLY or fallback to closing SmartApply tab.
        """
        try:
            WebDriverWait(self.driver, 5).until(
                lambda d: "post-apply" in d.current_url.lower()
            )
            print("POST_APPLY page detected. Closing tab...")
            self.driver.close()
        except:
            print("POST_APPLY not detected. Closing current tab anyway.")
            self.driver.close()
        time.sleep(1)
