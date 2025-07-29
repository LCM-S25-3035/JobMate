import os
import shutil
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException

class BrowserManager:
    def __init__(self, driver_path, profile_path):
        self.driver_path = os.path.abspath(driver_path)
        self.profile_path = os.path.abspath(profile_path)
        self.page_counter = 0

        # Load config from environment variables
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")
        self.use_temp_profile = os.getenv("USE_TEMP_PROFILE", "false").lower() == "true"
        self.original_profile_path = os.getenv("ORIGINAL_PROFILE_PATH")

        # Clone original profile if needed
        if self.use_temp_profile:
            self._clone_profile_to_temp()

        # Launch browser
        self.driver = self._launch_browser()

    def _clone_profile_to_temp(self):
        """Clone original Chrome profile to temp folder."""
        if not os.path.exists(self.profile_path):
            print(f"Cloning Chrome profile from {self.original_profile_path} to {self.profile_path}...")
            try:
                shutil.copytree(self.original_profile_path, self.profile_path, dirs_exist_ok=True)

                # Remove Chrome lockfiles from cloned profile
                for lock_file in ["SingletonCookie", "SingletonLock", "SingletonSocket"]:
                    lock_path = os.path.join(self.profile_path, lock_file)
                    if os.path.exists(lock_path):
                        os.remove(lock_path)
                        print(f"Deleted {lock_file} from temp profile.")
            except Exception as e:
                print(f"Error cloning Chrome profile: {e}")
        else:
            print(f"Temp Chrome profile already exists at {self.profile_path}, reusing it.")

    def _launch_browser(self):
        print("Launching browser with Undetected ChromeDriver...")
        try:
            driver = uc.Chrome(
                user_data_dir=self.profile_path,
                headless=False,  # Keep browser visible for login
            )
            print("Browser launched successfully.")
            return driver
        except Exception as e:
            print(f"Error launching Undetected ChromeDriver: {e}")
            raise

    def quit(self):
        input("Press Enter to quit the browser...")
        self.driver.quit()

    def scroll_into_view(self, element):
        """Scroll an element into view."""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            print("Scrolled element into view.")
        except Exception as e:
            print(f"Error scrolling element into view: {e}")

    def is_element_blocked(self, element):
        """
        Check if the given element is covered by a modal or overlay.
        """
        try:
            element_rect = element.rect
            x = element_rect['x'] + element_rect['width'] / 2
            y = element_rect['y'] + element_rect['height'] / 2

            # Find topmost element at the center point of the target element
            top_element = self.driver.execute_script(
                "return document.elementFromPoint(arguments[0], arguments[1]);", x, y
            )

            if element != top_element and top_element:
                print(f"Element is blocked by: {top_element.tag_name} ({top_element.get_attribute('class')})")
                return True
            return False
        except Exception as e:
            print(f"Error checking if element is blocked: {e}")
            return False
        
    def click_element(self, element, site_modal_handler=None):
        """Safely scroll into view and click an element, handling intercepts."""
        try:
            self.scroll_into_view(element)
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(element))

            # Check if element is blocked
            if self.is_element_blocked(element):
                print("Element is blocked. Checking for modals...")
                if site_modal_handler:
                    site_modal_handler()  # Call site-specific modal handler
                self.handle_generic_popups()
                time.sleep(1)  # Let UI settle
                self.scroll_into_view(element)

            element.click()
            print("Clicked element successfully.")

        except ElementClickInterceptedException:
            print("Click intercepted. Retrying after dismissing modals...")
            if site_modal_handler:
                site_modal_handler()
            self.handle_generic_popups()
            time.sleep(1)
            self.scroll_into_view(element)
            element.click()
            print("Clicked element successfully after retry.")

        except Exception as e:
            print(f"Error clicking element: {e}")
            raise


    def find_and_click_dynamic_button(self, target_text, site_modal_handler=None):
        """
        Find a button by text (case-insensitive) and click it.
        """
        print(f"Searching for button with text: '{target_text}'")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//*"))
            )
            buttons = self.driver.find_elements(
                By.XPATH, "//*[self::button or @role='button' or @onclick or @tabindex='0']"
            )
            for btn in buttons:
                try:
                    text = btn.text.strip() or btn.get_attribute("innerText").strip()
                    aria_label = btn.get_attribute("aria-label")
                    combined_text = text
                    if aria_label and aria_label.lower() != text.lower():
                        combined_text += f" {aria_label}"
                    combined_text = combined_text.strip()

                    if combined_text.lower() == target_text.lower():
                        print(f"Found button '{combined_text}', clicking...")
                        self.click_element(btn, site_modal_handler=site_modal_handler)
                        time.sleep(2)
                        return True
                except Exception as inner_e:
                    print(f"Skipped element due to error: {inner_e}")
            print(f"No button found with text: '{target_text}'")
            return False
        except Exception as e:
            print(f"Error finding/clicking button: {e}")
            return False

    def handle_generic_popups(self):
        """
        Attempt to close generic popups like cookie banners or modal dialogs.
        """
        print("Checking for generic popups...")
        try:
            # Example: Cookie consent
            cookie_btns = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree')]")
            for btn in cookie_btns:
                try:
                    self.click_element(btn)
                    print("Closed cookie consent popup.")
                    return True
                except:
                    continue
            # Example: Modal close buttons
            close_btns = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Close') or @aria-label='Close']")
            for btn in close_btns:
                try:
                    self.click_element(btn)
                    print("Closed modal popup.")
                    return True
                except:
                    continue
            print("No generic popups detected.")
            return False
        except Exception as e:
            print(f"Error handling popups: {e}")
            return False



