import os
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementNotInteractableException, WebDriverException

class FormFiller:
    def __init__(self, driver, navigation_manager, application_submitter):
        self.driver = driver
        self.navigation = navigation_manager
        self.submitter = application_submitter

    def fill_inputs_from_config_and_continue(self, inputs_data):
        """
        Fill mandatory inputs from config.json only if fields are empty,
        then scroll, tab through fields, and click 'Continue' on the new tab.
        """
        try:
            print("Checking and filling mandatory fields from config...")
            for field in inputs_data.get("inputs", []):
                name = field.get("name")
                placeholder = field.get("placeholder", "")

                # Skip optional fields
                if "optional" in placeholder.lower():
                    print(f"Skipping optional field: {name}")
                    continue

                # Get value from config
                value = os.getenv(name.upper())
                if not value:
                    print(f"No value found in config for '{name}', skipping...")
                    continue

                # Find the input field
                input_elem = self.driver.find_element(By.NAME, name)
                existing_value = input_elem.get_attribute("value").strip()

                if existing_value:
                    print(f"Field '{name}' already has value '{existing_value}', skipping...")
                    continue

                # Fill the field with config value
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_elem)
                time.sleep(random.uniform(0.3, 0.8))  # 🆕 Simulate human hesitation
                for char in value:
                    input_elem.send_keys(char)
                    time.sleep(random.uniform(0.1, 0.3))  # 🆕 Simulate human typing

                input_elem.send_keys(Keys.TAB)
                print(f"Filled '{name}' field.")

            print("Finished checking and filling fields.")
            time.sleep(random.uniform(0.5, 1.2))

            # TAB through all inputs to trigger any validation
            print("Tabbing through all inputs to trigger validation...")
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            for elem in all_inputs:
                try:
                    elem.send_keys(Keys.TAB)
                    time.sleep(0.1)
                except (StaleElementReferenceException, ElementNotInteractableException, WebDriverException) as e:
                    print(f"Warning: Could not tab through element: {e}")
                    continue

            # Scroll down to reveal Continue button
            self.navigation._handle_resume_upload_or_continue()

            # Attempt clicking Continue
            print("Attempting to click Continue...")
            time.sleep(random.uniform(0.3, 0.8))
            self.navigation._auto_continue_until_review()

            # After reaching review page, submit application
            print("Detected review page. Submitting application...")
            self.submitter.submit_application_review()

            # Switch back to original tab or reload job listings if needed
            if len(self.driver.window_handles) > 1:
                self.navigation._switch_back_to_main_tab()
                print("Switched back to original job listings tab.")
                print("Waiting 5 seconds to verify tab stays open...")
                time.sleep(5)
                print("Current window handles:", self.driver.window_handles)
            else:
                print("Original job listings tab was closed. Reloading job listings page...")
                listings_url = os.getenv("GLASSDOOR_URL") or os.getenv("INDEED_URL")
                if listings_url:
                    self.driver.get(listings_url)
                    time.sleep(3)
                    print("Job listings page reloaded.")
                else:
                    print("No fallback URL provided. Cannot reload listings page.")

        except Exception as e:
            print(f"Error while filling inputs or clicking continue: {e}")

    def handle_dynamic_questions(self):
        """
        Handles dynamic questions pages by filling inputs and force-clicking Continue
        until the review page is reached.
        """
        while True:
            current_url = self.driver.current_url
            if "smartapply.indeed.com/beta/indeedapply/form/questions-module/questions" in current_url:
                print(f"Detected questions page: {current_url}")

                # Fill all text inputs with default answers or config
                question_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea")
                for q_index, input_elem in enumerate(question_inputs, start=1):
                    placeholder = input_elem.get_attribute("placeholder")
                    name = input_elem.get_attribute("name")
                    answer = os.getenv(name.upper())
                    if not answer:
                        print(f"No config value for '{name}', skipping...")
                        continue

                    print(f"Answering question {q_index} ({name or placeholder}): {answer}")
                    input_elem.clear()
                    input_elem.send_keys(answer)
                    time.sleep(0.2)

                # Find the Continue button
                print("Looking for Continue button...")
                continue_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Continue')]"))
                )

                # Force enable the button if it's disabled
                is_disabled = continue_button.get_attribute("disabled")
                if is_disabled:
                    print("Continue button is disabled. Forcing it to be enabled...")
                    self.driver.execute_script("arguments[0].removeAttribute('disabled');", continue_button)
                    time.sleep(0.2)

                # Scroll into view and force click
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
                self.driver.execute_script("arguments[0].click();", continue_button)
                print("Forced click on Continue button.")

                # Wait for the next page
                time.sleep(2)

            else:
                print("No more questions pages detected. Proceeding to review page.")
                break

    def fill_questions_from_config(self, questions_data):
        """
        Fills dynamic questions using answers from config.json
        """
        print("Filling questions dynamically from config...")
        for question in questions_data.get("questions", []):
            question_text = question.get("question_text")
            input_info = question.get("input", {})
            input_name = input_info.get("name")

            # Convert question text to config key
            config_key = question_text.strip().replace(" ", "").upper()
            answer = os.getenv(config_key)

            if not answer:
                print(f"No config value found for '{question_text}' (key: {config_key}), skipping...")
                continue

            print(f"Typing '{answer}' into '{question_text}'...")

            # Find and type into the input
            try:
                input_elem = self.driver.find_element(By.NAME, input_name)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_elem)
                input_elem.clear()
                for char in answer:
                    input_elem.send_keys(char)
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error typing into '{question_text}': {e}")