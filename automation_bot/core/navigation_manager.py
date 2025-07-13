import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NavigationManager:
    def __init__(self, driver, browser_manager):
        self.driver = driver
        self.browser_manager = browser_manager

    def open_homepage(self, url):
        """Open homepage and scrape initial page buttons."""
        print(f"Opening homepage: {url}")
        self.driver.get(url)
        time.sleep(3)

    def switch_to_new_tab(self):
        """
        Switch to the new tab and scrape its inputs/buttons immediately.
        """
        print("Switching to new browser tab...")
        original_window = self.driver.current_window_handle
        all_windows = self.driver.window_handles

        if len(all_windows) > 1:
            new_tab = [w for w in all_windows if w != original_window][0]
            self.driver.switch_to.window(new_tab)
            print("Switched to new tab.")

            # Close the tab immediately if it's already a POST_APPLY redirect
            if self._close_post_apply_tab_if_needed():
                print("Closed POST_APPLY tab right after switching.")
                return False
            
            # Increment page counter for new tab
            self.browser_manager.page_counter += 1
            return True
        else:
            print("No new tab found.")
            return False

    def _switch_back_to_main_tab(self):
        """Switch back to original job listings tab."""
        try:
            all_windows = self.driver.window_handles
            print(f"Current window handles: {all_windows}")

            # Go back to the first tab
            original_window = all_windows[0]
            self.driver.switch_to.window(original_window)
            print("Switched back to original job listings tab.")
            time.sleep(2)

        except Exception as e:
            print(f"Error switching back to main tab: {e}")

    def _handle_resume_upload_or_continue(self):
        """Handles resume page or clicks Continue if present."""
        current_url = self.driver.current_url
        print(f"Current SmartApply URL: {current_url}")

        if ("resume-module/upload" in current_url or "form/resume" in current_url) and "relevant-experience" not in current_url:
            self.handle_resume_selection()
        else:
            try:
                print("Looking for 'Continue' button (waiting up to 5s)...")
                continue_button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Continue')]"))
                )
                if continue_button.get_attribute("disabled"):
                    print("Continue button is disabled. Enabling...")
                    self.driver.execute_script("arguments[0].removeAttribute('disabled');", continue_button)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
                self.driver.execute_script("arguments[0].click();", continue_button)
                print("Clicked 'Continue' button.")
                time.sleep(2)
            except Exception:
                print("No 'Continue' button detected.")
                print("Please manually click the Continue button in your browser.")
                input("Press Enter here once you have clicked Continue...")


    def handle_resume_selection(self):
        """
        On the resume page: select resume and click Continue properly.
        """
        current_url = self.driver.current_url
        print(f"Current SmartApply URL: {current_url}")

        if ("resume-module/upload" in current_url or "form/resume" in current_url) and "relevant-experience" not in current_url:
            print("On resume page. Selecting existing resume...")

            try:
                # Step 1: Click the resume card label
                print("Attempting to select the uploaded resume card...")
                resume_label = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//label[contains(@data-testid, 'FileResumeCard-label')]")
                    )
                )
                self.browser_manager.scroll_into_view(resume_label)
                resume_label.click()
                print("Clicked resume card label successfully.")

                # Confirm selection (check data-checked attribute)
                resume_card = self.driver.find_element(By.XPATH, "//div[@data-testid='FileResumeCard']")
                is_selected = resume_card.get_attribute("data-checked")
                if is_selected == "true":
                    print("Resume card is selected.")
                else:
                    print("Resume card not selected. Retrying...")
                    resume_label.click()

                # Step 2: Scroll to footer
                print("Scrolling to page footer to reveal Continue button...")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

                # Step 3: Find all Continue buttons
                continue_buttons = self.driver.find_elements(
                    By.XPATH, "//button[.//span[text()='Continue']]"
                )
                print(f"Found {len(continue_buttons)} Continue buttons.")

                # Step 4: Click the first visible and enabled Continue
                clicked = False
                for btn in continue_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        self.browser_manager.scroll_into_view(btn)
                        btn.click()
                        print("Clicked the correct Continue button.")
                        clicked = True
                        break

                if not clicked:
                    print("No visible Continue button found. Asking user for manual intervention.")
                    input("Please manually click Continue, then press Enter here to proceed.")

                time.sleep(2)  # Let page load

            except Exception as e:
                print(f"Error handling resume page: {e}")
                input("Please manually select your resume and click Continue in the browser, then press Enter to continue...")

        else:
            print("Not on resume page. Skipping resume selection.")

    def _click_continue_button(self):
        """
        Scrolls to and force-clicks the Continue button.
        """
        try:
            print("Looking for 'Continue' button...")
            continue_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Continue')]"))
            )
            if continue_button.get_attribute("disabled"):
                print("Continue button is disabled. Forcing it to be enabled...")
                self.driver.execute_script("arguments[0].removeAttribute('disabled');", continue_button)
                time.sleep(0.2)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
            self.driver.execute_script("arguments[0].click();", continue_button)
            print("Clicked 'Continue' button.")
        except Exception as e:
            print(f"Error clicking 'Continue' button: {e}")

    def _auto_continue_until_review(self, max_steps=2):
        """
        Click 'Continue' repeatedly until reaching review page.
        If the URL doesn't change after a click, pause and ask user for input.
        """
        steps = 0
        while steps < max_steps:
            current_url = self.driver.current_url
            print(f"Current SmartApply URL: {current_url}")

            if "smartapply.indeed.com/beta/indeedapply/form/review" in current_url:
                print("Reached review page.")
                break

            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                print("Looking for 'Continue' button...")
                continue_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue')]"))
                )
                if continue_button.get_attribute("disabled"):
                    print("Continue button is disabled. Enabling...")
                    self.driver.execute_script("arguments[0].removeAttribute('disabled');", continue_button)
               
                # Save URL before clicking
                previous_url = self.driver.current_url

                self.driver.execute_script("arguments[0].click();", continue_button)
                print("Clicked 'Continue' button.")
                time.sleep(3)

                # Check if URL changed
                new_url = self.driver.current_url
                if new_url == previous_url:
                    print("URL did not change after clicking Continue.")
                    print("There are mandatory fields that user need to input.")
                    input("Please fill missing values and press Enter to retry...")
                    print("Retrying click after manual input...")
                    self.driver.execute_script("arguments[0].click();", continue_button)
                    time.sleep(3)

                    # Check URL again
                    if self.driver.current_url == previous_url:
                        print("Still on same page after retry. Exiting loop.")
                        return
                    else:
                        print(f"URL changed to: {self.driver.current_url}")

                else:
                    print(f"URL changed to: {new_url}")
                steps += 1

            except Exception:
                print("No 'Continue' button found or click failed.")
                input("Click Continue in browser and press Enter here...")
                steps += 1

    def _close_post_apply_tab_if_needed(self):
        """Closes POST_APPLY tab if detected."""
        current_url = self.driver.current_url.lower()
        if "post-apply" in current_url or "smart-apply-action=post_apply" in current_url:
            print(f"Detected POST_APPLY redirect at {current_url}. Closing this tab...")
            self.driver.close()
            time.sleep(1)
            return True
        return False