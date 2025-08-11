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
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue')]") )
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
                self.driver.execute_script("arguments[0].click();", continue_button)
                print("Successfully clicked Continue button.")
                time.sleep(2)  # Wait for page transition
            except Exception as e:
                print(f"Error clicking Continue button: {e}")

            # Wait for review page to load (up to 3 minutes)
            print("Waiting for review page to load (up to 3 minutes)...")
            import datetime
            start_time = datetime.datetime.now()
            max_wait_seconds = 180
            review_url = "smartapply.indeed.com/beta/indeedapply/form/review"
            questions_url = "smartapply.indeed.com/beta/indeedapply/form/questions-module/questions"
            while (datetime.datetime.now() - start_time).total_seconds() < max_wait_seconds:
                current_url = self.driver.current_url
                if review_url in current_url:
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
                    return
                elif questions_url in current_url:
                    print(f"Landed on questions page: {current_url}")
                    print("Calling handle_dynamic_questions() to process questions...")
                    self.handle_dynamic_questions()
                    return
                else:
                    print(f"Current URL: {current_url} (not review or questions page). Waiting...")
                    time.sleep(3)
            print("Timeout: Review page did not load within 3 minutes. Exiting.")
            return

        except Exception as e:
            print(f"Error while filling inputs or clicking continue: {e}")

    def handle_dynamic_questions(self):
        """
        Handles dynamic questions pages by intelligently filling inputs based on
        question content and clicking Continue until the review page is reached.
        Prevents endless loops by checking if the URL changes after clicking Continue.
        Mimics human behavior with random scrolling, pauses, and focus changes.
        """
        import random
        max_attempts = 2  # Only try to answer and continue twice before giving up
        attempts = 0
        while attempts < max_attempts:
            current_url = self.driver.current_url
            if "smartapply.indeed.com/beta/indeedapply/form/questions-module/questions" in current_url:
                print(f"Detected questions page: {current_url}")

                # Mimic human: random scroll up/down before answering
                scroll_amount = random.randint(-200, 400)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.3, 1.2))

                # Find all question containers with their labels and inputs
                question_containers = self.driver.find_elements(By.CSS_SELECTOR, ".ia-Questions-item, [id^='q_']")
                unanswered_questions = 0
                if question_containers:
                    for idx, container in enumerate(question_containers, 1):
                        try:
                            # Mimic human: scroll to question, random pause
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
                            time.sleep(random.uniform(0.2, 0.7))
                            if random.random() < 0.2:
                                # Occasionally click on the question label
                                try:
                                    label_elem = container.find_element(By.CSS_SELECTOR, "label, .ia-Questions-label")
                                    label_elem.click()
                                except Exception:
                                    pass
                            label_elem = container.find_element(By.CSS_SELECTOR, "label, .ia-Questions-label")
                            question_text = label_elem.text.strip()
                            # Try to find input or radio
                            input_elems = container.find_elements(By.CSS_SELECTOR, "input, textarea")
                            radio_buttons = [el for el in input_elems if el.get_attribute("type") == "radio"]
                            if radio_buttons:
                                answered = self._handle_radio_question(container, question_text, radio_buttons, idx)
                                if not answered:
                                    unanswered_questions += 1
                            else:
                                # Text input/textarea
                                input_elem = input_elems[0] if input_elems else None
                                if input_elem and not input_elem.get_attribute("value"):
                                    answer = self._get_smart_answer(question_text)
                                    if answer:
                                        print(f"Answering question {idx}: {question_text[:50]}... -> {answer}")
                                        input_elem.clear()
                                        # Mimic human: type slowly
                                        for char in answer:
                                            input_elem.send_keys(char)
                                            time.sleep(random.uniform(0.08, 0.22))
                                        if random.random() < 0.15:
                                            # Occasionally click outside input
                                            self.driver.execute_script("window.scrollBy(0, 50);")
                                            time.sleep(random.uniform(0.1, 0.3))
                                    else:
                                        print(f"No answer found for question {idx}: {question_text[:50]}...")
                                        unanswered_questions += 1
                                    # Mimic human: random pause after each question
                                    time.sleep(random.uniform(0.2, 0.7))
                        except Exception as e:
                            from selenium.common.exceptions import NoSuchWindowException, WebDriverException
                            if isinstance(e, (NoSuchWindowException, WebDriverException)):
                                print(f"[Info] Window closed or not found while processing question {idx}, skipping error details.")
                            else:
                                print(f"Error processing question container {idx}: {e}")
                            continue
                else:
                    # Fallback to basic input finding
                    question_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea")
                    for q_index, input_elem in enumerate(question_inputs, 1):
                        try:
                            # Mimic human: scroll to input, random pause
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_elem)
                            time.sleep(random.uniform(0.2, 0.7))
                            placeholder = input_elem.get_attribute("placeholder") or ""
                            name = input_elem.get_attribute("name") or ""
                            if input_elem.get_attribute("value"):
                                continue
                            answer = os.getenv(name.upper()) or self._get_smart_answer(placeholder + " " + name)
                            if answer:
                                print(f"Answering question {q_index} ({name or placeholder}): {answer}")
                                input_elem.clear()
                                for char in answer:
                                    input_elem.send_keys(char)
                                    time.sleep(random.uniform(0.08, 0.22))
                                if random.random() < 0.15:
                                    self.driver.execute_script("window.scrollBy(0, 50);")
                                    time.sleep(random.uniform(0.1, 0.3))
                            else:
                                print(f"No answer found for question {q_index} ({name or placeholder})")
                                unanswered_questions += 1
                            time.sleep(random.uniform(0.2, 0.7))
                        except Exception as e:
                            print(f"Error filling input {q_index}: {e}")
                            continue

                # Mimic human: random scroll before clicking Continue
                scroll_amount = random.randint(-100, 200)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.3, 1.0))

                # After attempting to answer, try to click Continue
                prev_url = self.driver.current_url
                self._click_continue_button()
                # Wait for URL to change (max 10s)
                url_changed = False
                for _ in range(20):  # 20 x 0.5s = 10s
                    time.sleep(0.5)
                    if self.driver.current_url != prev_url:
                        url_changed = True
                        break
                if url_changed:
                    # Page advanced, break loop
                    print("Questions page advanced after clicking Continue.")
                    return True
                else:
                    print(f"Mandatory fields found. No answers for {unanswered_questions} question(s). Closing current job tab.")
                    # Mimic human: wait a random short time before closing tab
                    time.sleep(random.uniform(0.5, 1.5))
                    self.driver.close()
                    # Switch back to main tab if available
                    if len(self.driver.window_handles) > 0:
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    return False
            else:
                # Not on questions page, break loop
                print(f"Not on questions page anymore: {current_url}")
                return True
            attempts += 1
        print("Max attempts reached for questions page. Exiting questions handler.")
        return False

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

        # First name
        if any(keyword in question_lower for keyword in ["first name", "firstname", "given name"]):
            return self.config.get("firstName", "")

        # Last name
        if any(keyword in question_lower for keyword in ["last name", "lastname", "surname", "family name"]):
            return self.config.get("lastName", "")

        # Phone number
        if any(keyword in question_lower for keyword in ["phone", "phone number", "mobile", "cell"]):
            return self.config.get("phoneNumber", "")

        # Email address
        if any(keyword in question_lower for keyword in ["email", "e-mail", "email address"]):
            return self.config.get("email", "")

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

        # Years of BI Development experience
        if ("bi development" in question_lower or "business intelligence" in question_lower) and "year" in question_lower:
            return config_answers.get("years_experience_bi_development", "3")

        # French & English language question
        if ("french" in question_lower and "english" in question_lower) or ("francais" in question_lower and "anglais" in question_lower):
            return config_answers.get("language_french_english", "English only")
        
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
        
        # Address and city questions
        if any(keyword in question_lower for keyword in ["address", "location", "where do you live", "current address"]):
            # Prefer current_city if question asks for city, else use address
            if "city" in question_lower:
                return config_answers.get("current_city", "Mississauga")
            return config_answers.get("address", "Toronto")
        

        # Gender
        if any(keyword in question_lower for keyword in ["gender", "sex"]):
            return config_answers.get("gender", "Female")

        # Ethnicity
        if any(keyword in question_lower for keyword in ["ethnicity", "race", "origin"]):
            return config_answers.get("ethnicity", "South East Asian")

        # Disability
        if any(keyword in question_lower for keyword in ["disability", "disabled", "impairment"]):
            return config_answers.get("disability", "No")

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
        
        # FUZZY MATCHING FALLBACK (only if exact matching failed)
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
            ("graduation date", ["graduation_date"]),
            ("gender", ["gender"]),
            ("ethnicity", ["ethnicity"]),
            ("disability", ["disability"]),
            ("current city", ["current_city"]),
            ("postal code", ["postal_code"]),
            ("willing to travel", ["willing_to_travel"]),
            ("driver license", ["driver_license"]),
            ("available weekends", ["available_weekends"])
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