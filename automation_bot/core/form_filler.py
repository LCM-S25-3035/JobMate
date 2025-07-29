import os
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementNotInteractableException, WebDriverException
try:
    from fuzzywuzzy import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False

class FormFiller:
    def __init__(self, driver, navigation_manager, application_submitter, config=None):
        self.driver = driver
        self.navigation = navigation_manager
        self.submitter = application_submitter
        self.config = config or {}

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
            
            # Simple continue button click instead of auto-continue-until-review
            try:
                continue_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue')]"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
                self.driver.execute_script("arguments[0].click();", continue_button)
                print("Successfully clicked Continue button.")
                time.sleep(2)  # Wait for page transition
            except Exception as e:
                print(f"Error clicking Continue button: {e}")

            # Check if we're actually on review page before submitting
            current_url = self.driver.current_url
            if "smartapply.indeed.com/beta/indeedapply/form/review" in current_url:
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
            elif "smartapply.indeed.com/beta/indeedapply/form/questions-module/questions" in current_url:
                print(f"Landed on questions page: {current_url}")
                print("Calling handle_dynamic_questions() to process questions...")
                self.handle_dynamic_questions()
            else:
                print(f"Not on review or questions page. Current URL: {current_url}")

        except Exception as e:
            print(f"Error while filling inputs or clicking continue: {e}")

    def handle_dynamic_questions(self):
        """
        Handles dynamic questions pages by intelligently filling inputs based on
        question content and clicking Continue until the review page is reached.
        """
        while True:
            current_url = self.driver.current_url
            if "smartapply.indeed.com/beta/indeedapply/form/questions-module/questions" in current_url:
                print(f"Detected questions page: {current_url}")

                # Find all question containers with their labels and inputs
                question_containers = self.driver.find_elements(By.CSS_SELECTOR, ".ia-Questions-item, [id^='q_']")
                
                if not question_containers:
                    # Fallback to basic input finding
                    question_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea")
                    self._fill_basic_inputs(question_inputs)
                else:
                    # Smart question answering
                    success = self._fill_intelligent_questions(question_containers)
                    if not success:
                        # Questions couldn't be answered, tab was closed
                        return False

                # Find and click Continue button
                self._click_continue_button()
                
                # Wait for next page
                time.sleep(2)
            else:
                print("No more questions pages detected. Proceeding to review page.")
                break
        
        return True  # Successfully processed all questions

    def _fill_intelligent_questions(self, question_containers):
        """
        Intelligently fills questions based on their content
        """
        print(f"Found {len(question_containers)} question containers")
        
        unanswered_questions = 0
        
        for idx, container in enumerate(question_containers, 1):
            try:
                # Extract question text from label
                label_elem = container.find_element(By.CSS_SELECTOR, "label, [data-testid*='label']")
                question_text = label_elem.text.strip().lower()
                
                # Check for radio buttons first
                radio_buttons = container.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                if radio_buttons:
                    # Handle radio button questions
                    if self._handle_radio_question(container, question_text, radio_buttons, idx):
                        continue
                    else:
                        print(f"Question {idx}: '{question_text[:50]}...' -> No smart answer found for radio buttons")
                        unanswered_questions += 1
                        continue
                
                # Find input field in this container (text/textarea)
                try:
                    input_elem = container.find_element(By.CSS_SELECTOR, "input[type='text'], textarea, input:not([type='hidden']):not([type='radio'])")
                except:
                    # No text input found, skip this question
                    print(f"Question {idx}: No text input or radio buttons found")
                    continue
                
                # Skip if already filled
                if input_elem.get_attribute("value"):
                    print(f"Question {idx} already filled, skipping")
                    continue
                
                # Determine answer based on question content
                answer = self._get_smart_answer(question_text)
                
                if answer:
                    print(f"Question {idx}: '{question_text[:50]}...' -> Answer: '{answer}'")
                    
                    # Scroll into view and fill
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_elem)
                    time.sleep(0.2)
                    
                    input_elem.clear()
                    input_elem.send_keys(answer)
                    time.sleep(0.3)
                    
                    # Trigger change event
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", input_elem)
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", input_elem)
                else:
                    print(f"Question {idx}: '{question_text[:50]}...' -> No smart answer found")
                    unanswered_questions += 1
                    
            except Exception as e:
                print(f"Error processing question container {idx}: {e}")
                continue
        
        # If there are unanswered questions, skip this job
        if unanswered_questions > 0:
            print(f"No answer found for {unanswered_questions} question(s). Skipping auto apply, and closing the tab.")
            time.sleep(random.uniform(0.5, 1.5))  # Wait shorter random seconds
            
            # Close the current tab
            self.driver.close()
            
            # Switch back to the main tab if there are multiple tabs
            if len(self.driver.window_handles) > 0:
                self.driver.switch_to.window(self.driver.window_handles[0])
                print("Switched back to main job listings tab.")
            
            return False  # Indicate that the job was skipped
        
        return True  # All questions answered successfully

    def _handle_radio_question(self, container, question_text, radio_buttons, question_idx):
        """
        Handle radio button questions by selecting appropriate option
        """
        # Check if already selected
        for radio in radio_buttons:
            if radio.is_selected():
                print(f"Question {question_idx} (radio) already selected, skipping")
                return True
        
        # Get answer based on question content
        answer = self._get_smart_answer(question_text)
        
        if not answer:
            return False  # No answer found
        
        # Find the appropriate radio button to click
        answer_lower = answer.lower().strip()
        
        for radio in radio_buttons:
            try:
                # Get the label text for this radio button
                radio_label = radio.find_element(By.XPATH, "./following-sibling::span | ./parent::label//span").text.strip().lower()
                
                # Match common patterns
                if (answer_lower == "yes" and radio_label == "yes") or \
                   (answer_lower == "no" and radio_label == "no") or \
                   (answer_lower in radio_label or radio_label in answer_lower):
                    
                    print(f"Question {question_idx}: '{question_text[:50]}...' -> Selecting: '{radio_label}'")
                    
                    # Scroll into view and click
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio)
                    time.sleep(0.2)
                    self.driver.execute_script("arguments[0].click();", radio)
                    time.sleep(0.3)
                    
                    return True
                    
            except Exception as e:
                print(f"Error processing radio button: {e}")
                continue
        
        return False  # No matching radio button found

    def _get_smart_answer(self, question_text):
        """
        Returns appropriate answer based on question content
        """
        question_lower = question_text.lower()
        
        # Load answers from config
        config_answers = self.config.get("question_answers", {})
        
        # LinkedIn profile questions
        if any(keyword in question_lower for keyword in ["linkedin", "profile"]):
            return config_answers.get("linkedin_profile", "https://www.linkedin.com/in/chaw-thinn")
        
        # Salary expectations
        if any(keyword in question_lower for keyword in ["salary", "compensation", "pay", "wage"]):
            return config_answers.get("salary_expectations", "$65,000 - $75,000 CAD")
        
        # Years of experience - specific roles
        if "data analyst" in question_lower and "year" in question_lower:
            return config_answers.get("years_experience_data_analyst", "2")
        
        if "software" in question_lower and "year" in question_lower:
            return config_answers.get("years_experience_software", "3")
        
        if "developer" in question_lower and "year" in question_lower:
            return config_answers.get("years_experience_developer", "3")
        
        if "python" in question_lower and "year" in question_lower:
            return config_answers.get("years_experience_python", "3")
        
        if "sql" in question_lower and "year" in question_lower:
            return config_answers.get("years_experience_sql", "2")
        
        # General experience
        if any(keyword in question_lower for keyword in ["year", "experience"]) and "professional" in question_lower:
            return config_answers.get("years_experience", "2-3")
        
        # Portfolio/Website
        if any(keyword in question_lower for keyword in ["portfolio", "website", "github"]):
            return config_answers.get("portfolio_website", "https://github.com/chawthinn")
        
        # Cover letter
        if any(keyword in question_lower for keyword in ["cover letter", "why", "interest"]):
            return config_answers.get("cover_letter", "I am excited to apply for this position as it aligns perfectly with my background in data analysis.")
        
        # Availability
        if any(keyword in question_lower for keyword in ["availability", "start", "when"]):
            return config_answers.get("availability", "Immediately")
        
        # Relocation
        if any(keyword in question_lower for keyword in ["relocate", "move"]):
            return config_answers.get("willing_to_relocate", "Yes")
        
        # Work authorization
        if any(keyword in question_lower for keyword in ["authorization", "eligible", "work", "visa"]):
            return config_answers.get("authorization_to_work", "Yes")
        
        # Sponsorship questions
        if any(keyword in question_lower for keyword in ["sponsorship", "sponsor", "visa sponsorship"]):
            return config_answers.get("require_sponsorship", "Yes")
        
        # Address questions
        if any(keyword in question_lower for keyword in ["address", "location", "where do you live", "current address"]):
            return config_answers.get("address", "Toronto")
        
        # Education
        if any(keyword in question_lower for keyword in ["degree", "education", "graduate"]):
            return config_answers.get("degree_completed", "Yes")
        
        if "graduation" in question_lower:
            return config_answers.get("graduation_date", "May 2023")
        
        if "gpa" in question_lower:
            return config_answers.get("gpa", "3.7")
        
        # Default fallback for yes/no questions
        if "?" in question_text and len(question_text.split()) < 15:
            if any(keyword in question_lower for keyword in ["eligible", "authorized", "able", "willing"]):
                return "Yes"
        
        # 🆕 FUZZY MATCHING FALLBACK (only if exact matching failed)
        if FUZZY_AVAILABLE:
            return self._fuzzy_fallback_answer(question_lower, config_answers)
        
        return None

    def _fuzzy_fallback_answer(self, question_lower, config_answers):
        """
        Fuzzy matching fallback when exact keyword matching fails
        """
        fuzzy_patterns = [
            ("years of experience", ["years_experience", "years_experience_data_analyst"]),
            ("salary expectation", ["salary_expectations"]),
            ("linkedin profile", ["linkedin_profile"]),
            ("work authorization", ["authorization_to_work"]),
            ("visa sponsorship", ["require_sponsorship"]),
            ("willing to relocate", ["willing_to_relocate"]),
            ("current address", ["address"]),
            ("portfolio website", ["portfolio_website"]),
            ("degree completed", ["degree_completed"]),
            ("graduation date", ["graduation_date"])
        ]
        
        for pattern, config_keys in fuzzy_patterns:
            if fuzz.partial_ratio(pattern, question_lower) > 75:  # 75% similarity threshold
                for key in config_keys:
                    if key in config_answers:
                        return config_answers[key]
        
        return None

    def _fill_basic_inputs(self, question_inputs):
        """
        Fallback method for basic input filling
        """
        for q_index, input_elem in enumerate(question_inputs, start=1):
            try:
                placeholder = input_elem.get_attribute("placeholder") or ""
                name = input_elem.get_attribute("name") or ""
                
                # Skip if already filled
                if input_elem.get_attribute("value"):
                    continue
                
                # Get answer from environment or config
                answer = os.getenv(name.upper()) or self._get_smart_answer(placeholder + " " + name)
                
                if answer:
                    print(f"Answering question {q_index} ({name or placeholder}): {answer}")
                    input_elem.clear()
                    input_elem.send_keys(answer)
                    time.sleep(0.2)
                else:
                    print(f"No answer found for question {q_index} ({name or placeholder})")
                    
            except Exception as e:
                print(f"Error filling input {q_index}: {e}")

    def _click_continue_button(self):
        """
        Find and click the Continue button
        """
        try:
            print("Looking for Continue button...")
            continue_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Continue')] | //button[@data-testid='continue-button']"))
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
            print("Successfully clicked Continue button.")
            
        except Exception as e:
            print(f"Error clicking Continue button: {e}")

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