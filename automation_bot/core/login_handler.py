import os
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginHandler:
    def __init__(self, driver, profile_path, page_counter=1):
        self.driver = driver
        self.profile_path = profile_path
        self.page_counter = page_counter
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")

    def dynamic_login(self):
        """Attempts to click a login button if found; otherwise, assumes already signed in."""
        print("Checking for login buttons...")

        try:
            # Scroll to top to ensure all buttons are visible
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)  # Reduced from 2 to 1 second - Wait for dynamic buttons to render

            print("Scraping visible buttons dynamically...")
            buttons = [
                btn.text.strip()
                for btn in self.driver.find_elements(By.XPATH, "//button | //*[@role='button']")
                if btn.text.strip()
            ]
            print(f"Buttons found on page: {buttons}")

        except Exception as e:
            print(f"Failed to scrape buttons: {e}")
            buttons = []

        # Detect login/register buttons
        login_keywords = ["sign in", "log in", "login", "register", "join", "create account"]
        
        # Find matching login buttons
        login_buttons = [btn for btn in buttons if any(keyword in btn.lower() for keyword in login_keywords)]
        
        if not login_buttons:
            print("No login buttons found. Assuming already signed in.")
            return False  # No login needed - already signed in
        
        # Attempt to click the first login button found
        for button_text in login_buttons:
            try:
                print(f"Attempting to click login button: {button_text}")
                xpath = f"//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{button_text.lower()}')]"
                login_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                login_button.click()
                print(f"Successfully clicked login button: {button_text}")
                return True  # Login button clicked - need to complete login flow
                
            except Exception as e:
                print(f"Failed to click button '{button_text}': {e}")
                continue
        
        # This should never happen based on user's feedback, but if it does, treat as login needed
        print("Login buttons found but couldn't click any - treating as login needed")
        return True

    def find_and_click_dynamic_button(self, target_text):
        """Find and click a button by exact text match."""
        print(f"Searching for clickable elements with text: '{target_text}'...")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//*"))
            )

            elements = self.driver.find_elements(
                By.XPATH, "//*[self::button or @role='button' or @onclick or @tabindex='0']"
            )
            for el in elements:
                try:
                    text = el.text.strip() or el.get_attribute("innerText").strip()
                    aria_label = el.get_attribute("aria-label")
                    combined_text = text
                    if aria_label and aria_label.lower() != text.lower():
                        combined_text += f" {aria_label}"
                    combined_text = combined_text.strip()

                    if combined_text.lower() == target_text.lower():
                        print(f"Clicking exact match element: '{combined_text}'")

                        self.driver.execute_script("arguments[0].scrollIntoView(true);", el)
                        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(el))
                        el.click()
                        time.sleep(1)  # Reduced from 2 to 1 second
                        return True

                except Exception as inner_e:
                    print(f"Skipped element due to error: {inner_e}")

            print(f"No element with text '{target_text}' found.")
            return False
        except Exception as e:
            print(f"Error while searching/clicking dynamic buttons: {e}")
            return False
        
    def fill_email_field(self):
        """Fill the email field with human-like typing."""
        try:
            # Try multiple selectors for email input
            email_selectors = [
                "//input[@type='email']",
                "//input[@data-test='emailInput-input']",
                "//input[contains(@name, 'email')]",
                "//input[contains(@id, 'email')]"
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = self.driver.find_element(By.XPATH, selector)
                    if email_input.is_displayed():
                        break
                except Exception:
                    continue
            
            if not email_input:
                print("No email input field found")
                return
                
            email_input.clear()
            for char in self.email:
                email_input.send_keys(char)
                time.sleep(0.1)  # Reduced from 0.2 to 0.1 seconds
            print(f"Filled email field with {self.email}")
        except Exception as e:
            print(f"Error filling email field: {e}")

    def fill_password_field(self):
        """Fill the password field with human-like typing."""
        try:
            # Try multiple selectors for password input
            password_selectors = [
                "//input[@type='password']",
                "//input[@data-test='passwordInput-input']",
                "//input[contains(@name, 'password')]",
                "//input[contains(@id, 'password')]"
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = self.driver.find_element(By.XPATH, selector)
                    if password_input.is_displayed():
                        break
                except Exception:
                    continue
            
            if not password_input:
                print("No password input field found")
                return
                
            password_input.clear()
            for char in self.password:
                password_input.send_keys(char)
                time.sleep(0.1)  # Reduced from 0.2 to 0.1 seconds
            print("Filled password field.")
            time.sleep(2)  # Reduced from 5 to 2 seconds - Let modal settle
        except Exception as e:
            print(f"Error filling password field: {e}")
