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
            from selenium.common.exceptions import NoSuchWindowException, WebDriverException
            if isinstance(e, (NoSuchWindowException, WebDriverException)):
                print("[Info] Window closed or not found while switching tabs.")
            else:
                print(f"Error switching back to main tab: {e}")

    def _handle_resume_upload_or_continue(self):
        """Handles resume page or clicks Continue if present."""
        current_url = self.driver.current_url
        print(f"Current SmartApply URL: {current_url}")

        # Debug: Show which conditions are being checked
        is_resume_upload = "resume-module/upload" in current_url
        is_form_resume = "form/resume" in current_url
        is_resumeapply = "resumeapply" in current_url  # New pattern for resumeapply URLs
        is_relevant_experience = "relevant-experience" in current_url
        
        print(f"URL condition check:")
        print(f"  - Contains 'resume-module/upload': {is_resume_upload}")
        print(f"  - Contains 'form/resume': {is_form_resume}")
        print(f"  - Contains 'resumeapply': {is_resumeapply}")
        print(f"  - Contains 'relevant-experience': {is_relevant_experience}")

        if (is_resume_upload or is_form_resume or is_resumeapply) and not is_relevant_experience:
            print("Detected resume page - calling handle_resume_selection()")
            self.handle_resume_selection()
        else:
            print("Not a resume page - looking for generic Continue button")
            # Wait randomly before clicking to allow page to finish loading
            import random
            wait_time = random.uniform(0.5, 2.5)
            print(f"Waiting {wait_time:.2f} seconds before searching for Continue button...")
            time.sleep(wait_time)
            # Try multiple selectors for Continue button (robust)
            continue_selectors = [
                "//button[contains(text(), 'Continue')]",  # Direct text match
                "//button[@type='submit']",  # Submit button
                "//button[.//span[text()='Continue']]",  # Span with Continue text
                "//button[@data-testid='ia-continueButton']",  # Indeed specific testid
                "//button[contains(@class, 'continue')]",  # Class-based
                "//input[@type='submit' and @value='Continue']",  # Input submit
                "//button[contains(@aria-label, 'Continue')]",  # Aria label
                "//form//button[@type='submit']"  # Form submit button
            ]
            clicked = False
            for selector in continue_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    print(f"Trying selector: {selector} - Found {len(buttons)} button(s)")
                    for btn in buttons:
                        print(f"Button text: '{btn.text}', displayed: {btn.is_displayed()}, enabled: {btn.is_enabled()}")
                        if btn.is_displayed() and btn.is_enabled():
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                            self.driver.execute_script("arguments[0].click();", btn)
                            print("Clicked 'Continue' button with selector:", selector)
                            clicked = True
                            time.sleep(2)
                            break
                    if clicked:
                        break
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
            if not clicked:
                print("No 'Continue' button detected with any selector.")
                print("Please manually click the Continue button in your browser.")
                input("Press Enter here once you have clicked Continue...")


    def handle_resume_selection(self):
        """
        On the resume page: select resume and click Continue properly.
        """
        current_url = self.driver.current_url
        print(f"Current SmartApply URL: {current_url}")

        if ("resume-module/upload" in current_url or "form/resume" in current_url or "resumeapply" in current_url) and "relevant-experience" not in current_url:
            print("On resume page. Selecting existing resume...")

            try:
                # Step 1: Try multiple selectors for the resume card based on current HTML
                print("Attempting to select the uploaded resume card...")
                resume_selectors = [
                    "//label[@data-testid='FileResumeCard-label']",  # Current structure
                    "//input[@data-testid='FileResumeCard-input']",  # Direct radio input
                    "//div[@data-testid='FileResumeCard']//label",   # Label within card
                    "//div[@data-testid='FileResumeCard']",          # Card div itself
                    "//label[contains(@data-testid, 'FileResumeCard-label')]",  # Original selector
                    "//div[@data-testid='FileResumeCard']//input[@type='radio']",  # Radio within card
                    "//input[@type='radio' and @name='resumeType' and @value='SAVED_FILE_RESUME']",  # By value
                    "//input[@type='radio' and contains(@name, 'resume')]/..",
                    "//div[contains(@class, 'ResumeCard')]//label",
                    "//label[contains(@class, 'resume') or contains(@for, 'resume')]"
                ]
                
                resume_element = None
                for selector in resume_selectors:
                    try:
                        resume_element = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        print(f"Found resume element with selector: {selector}")
                        break
                    except Exception:
                        continue
                
                if resume_element:
                    self.browser_manager.scroll_into_view(resume_element)
                    resume_element.click()
                    print("Clicked resume card/label successfully.")
                    time.sleep(1)  # Let selection register
                    
                    # Verify selection worked by checking data-checked attribute
                    try:
                        resume_card = self.driver.find_element(By.XPATH, "//div[@data-testid='FileResumeCard']")
                        is_checked = resume_card.get_attribute("data-checked")
                        print(f"Resume card data-checked status: {is_checked}")
                        
                        if is_checked != "true":
                            print("Resume not selected, trying to click the radio input directly...")
                            radio_input = self.driver.find_element(By.XPATH, "//input[@data-testid='FileResumeCard-input']")
                            self.browser_manager.scroll_into_view(radio_input)
                            radio_input.click()
                            time.sleep(1)
                            
                            # Check again
                            is_checked = resume_card.get_attribute("data-checked")
                            print(f"Resume card data-checked status after radio click: {is_checked}")
                    except Exception as verify_err:
                        print(f"Could not verify resume selection: {verify_err}")
                else:
                    print("Could not find resume card with any selector")
                    # Debug: show what elements are available
                    all_labels = self.driver.find_elements(By.TAG_NAME, "label")
                    all_divs = self.driver.find_elements(By.XPATH, "//div[contains(@data-testid, 'Card') or contains(@class, 'Card')]")
                    print(f"Found {len(all_labels)} labels and {len(all_divs)} card-like divs on page")
                    
                    # Show specific testid elements
                    testid_elements = self.driver.find_elements(By.XPATH, "//*[@data-testid]")
                    testids = [elem.get_attribute("data-testid") for elem in testid_elements if elem.get_attribute("data-testid")]
                    print(f"Elements with data-testid: {list(set(testids))}")

                # Step 2: Scroll to footer to reveal Continue button
                print("Scrolling to page footer to reveal Continue button...")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

                # Step 3: Try multiple selectors for Continue button
                continue_selectors = [
                    "//button[contains(text(), 'Continue')]",  # Direct text match
                    "//button[@type='submit']",  # Submit button
                    "//button[.//span[text()='Continue']]",  # Span with Continue text
                    "//button[@data-testid='ia-continueButton']",  # Indeed specific testid
                    "//button[contains(@class, 'continue')]",  # Class-based
                    "//input[@type='submit' and @value='Continue']",  # Input submit
                    "//button[contains(@class, 'ia-BasePage-component--withContinue')]//button",  # Within continue component
                    "//div[contains(@class, 'withContinue')]//button",  # Within continue div
                    "//button[contains(@aria-label, 'Continue')]",  # Aria label
                    "//form//button[@type='submit']"  # Form submit button
                ]
                
                clicked = False
                for selector in continue_selectors:
                    try:
                        continue_buttons = self.driver.find_elements(By.XPATH, selector)
                        print(f"Found {len(continue_buttons)} Continue buttons with selector: {selector}")
                        
                        for btn in continue_buttons:
                            if btn.is_displayed() and btn.is_enabled():
                                self.browser_manager.scroll_into_view(btn)
                                btn.click()
                                print("Clicked Continue button successfully.")
                                clicked = True
                                break
                        
                        if clicked:
                            break
                    except Exception as e:
                        print(f"Error with selector {selector}: {e}")
                        continue

                if not clicked:
                    print("No Continue button found with any selector. Manual intervention needed.")
                    input("Please manually click Continue, then press Enter here to proceed.")

                time.sleep(2)  # Let page load

            except Exception as e:
                from selenium.common.exceptions import NoSuchWindowException, WebDriverException
                if isinstance(e, (NoSuchWindowException, WebDriverException)):
                    print("[Info] Window closed or not found during resume selection.")
                else:
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
            from selenium.common.exceptions import NoSuchWindowException, WebDriverException
            if isinstance(e, (NoSuchWindowException, WebDriverException)):
                print("[Info] Window closed or not found while clicking Continue.")
            else:
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
                print(f"URL before Continue click: {previous_url}")

                self.driver.execute_script("arguments[0].click();", continue_button)
                print("Clicked 'Continue' button.")
                time.sleep(3)

                # Check if URL changed
                new_url = self.driver.current_url
                print(f"URL after Continue click: {new_url}")
                
                # Normalize URLs for comparison (remove protocol differences)
                def normalize_url(url):
                    return url.replace('https://', '').replace('http://', '').lower()
                
                previous_normalized = normalize_url(previous_url)
                new_normalized = normalize_url(new_url)
                
                # Check if we moved to a different page (path changed)
                url_changed = previous_normalized != new_normalized
                moved_to_review = 'form/review' in new_url
                
                if url_changed or moved_to_review:
                    print("Successfully navigated to next page.")
                    return
                else:
                    print("URL did not change after clicking Continue.")
                    print("There are mandatory fields that user need to input.")
                    input("Please fill missing values and press Enter to retry...")
                    print("Retrying click after manual input...")
                    self.driver.execute_script("arguments[0].click();", continue_button)
                    time.sleep(3)

                    # Check URL again
                    final_url = self.driver.current_url
                    final_normalized = normalize_url(final_url)
                    
                    if final_normalized != previous_normalized or 'form/review' in final_url:
                        print("Successfully navigated after retry.")
                        return
                    else:
                        print("Still on same page after retry. Exiting loop.")
                        return

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