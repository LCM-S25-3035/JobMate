import os
import json
from selenium.webdriver.common.by import By

class FormScraper:
    def __init__(self, driver, profile_path, page_counter=1):
        self.driver = driver
        self.profile_path = profile_path
        self.page_counter = page_counter

        # Ensure profile directory exists
        if not os.path.exists(self.profile_path):
            os.makedirs(self.profile_path)

    def scrape_page_buttons(self):
        """Scrape visible buttons from the page (excluding nav/footer)."""
        print("Scraping current page buttons...")
        data = {"buttons": []}
        try:
            navbars = self.driver.find_elements(By.XPATH, "//header | //nav | //footer")
            nav_buttons = set()
            for navbar in navbars:
                nav_btns = navbar.find_elements(By.XPATH, ".//button | .//*[@role='button']")
                for nav_btn in nav_btns:
                    nav_text = nav_btn.text.strip().lower()
                    if nav_text:
                        nav_buttons.add(nav_text)

            buttons = self.driver.find_elements(By.XPATH, "//button | //*[@role='button']")
            for btn in buttons:
                txt = btn.text.strip()
                if txt and txt.lower() not in nav_buttons:
                    data["buttons"].append(txt)

            print(f"Found {len(data['buttons'])} buttons on the page.")
        except Exception as e:
            print(f"Error scraping buttons: {e}")

        return data

    def scrape_all_buttons_on_page(self):
        """Scrape all <button> and elements with role='button' on the current page (not modal)."""
        print("Scraping all buttons on the page...")
        data = {"buttons": []}
        try:
            buttons = self.driver.find_elements(By.XPATH, "//button | //*[@role='button']")
            for btn in buttons:
                text = btn.text.strip()
                if text:
                    data["buttons"].append(text)
            print(f"Scraped {len(data['buttons'])} buttons from the page.")

            # Save to JSON
            filename = f"page_{self.page_counter}_buttons.json"
            filepath = os.path.join(self.profile_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Page button contents saved to {filepath}")

        except Exception as e:
            print(f"Error scraping page buttons: {e}")

        return data

    def scrape_modal_contents(self):
        """Scrape buttons and inputs from a modal/dialog if present."""
        print("Checking for modal contents...")
        data = {"buttons": [], "inputs": []}
        try:
            modal = self.driver.find_element(
                By.XPATH,
                "//div[contains(@class, 'modal') or contains(@class, 'dialog') or @role='dialog']"
            )
            # Scrape modal buttons
            buttons = modal.find_elements(By.XPATH, ".//button | .//*[@role='button']")
            for btn in buttons:
                txt = btn.text.strip()
                if txt:
                    data["buttons"].append(txt)
            # Scrape modal inputs
            inputs = modal.find_elements(By.XPATH, ".//input")
            for inp in inputs:
                type_attr = inp.get_attribute("type")
                placeholder = inp.get_attribute("placeholder")
                name = inp.get_attribute("name")
                if type_attr:
                    data["inputs"].append({"type": type_attr, "placeholder": placeholder, "name": name})
            print("Modal contents scraped.")
            
            # Save modal contents to JSON
            filename = f"modal_{self.page_counter}_contents.json"
            filepath = os.path.join(self.profile_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Modal contents saved to {filepath}")

        except Exception as _:
            print("No modal found or failed to scrape.")
        return data

    def scrape_all_inputs_on_page(self):
        """Scrape all <input> fields on the current page (not modal)."""
        print("Scraping all inputs on the page...")
        data = {"inputs": []}
        try:
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                name = inp.get_attribute("name")
                placeholder = inp.get_attribute("placeholder")
                type_attr = inp.get_attribute("type")
                if name or placeholder or type_attr:
                    data["inputs"].append({
                        "name": name,
                        "placeholder": placeholder,
                        "type": type_attr
                    })
            print(f"Scraped {len(data['inputs'])} input fields from the page.")

            # Save to JSON
            filename = f"page_{self.page_counter}_inputs.json"
            filepath = os.path.join(self.profile_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Page input contents saved to {filepath}")

        except Exception as e:
            print(f"Error scraping page inputs: {e}")

        return data

    def scrape_new_tab_inputs(self):
        """Scrape all input fields (name, placeholder, type) on the current page and export to JSON."""
        print("Scraping inputs from new tab page...")
        data = {"inputs": []}
        try:
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                name = inp.get_attribute("name")
                placeholder = inp.get_attribute("placeholder")
                type_attr = inp.get_attribute("type")
                data["inputs"].append({
                    "name": name,
                    "placeholder": placeholder,
                    "type": type_attr
                })
            print(f"Scraped {len(data['inputs'])} input fields from new tab.")

            # Save to JSON file
            filename = f"new_tab_inputs_{self.page_counter}.json"
            filepath = os.path.join(self.profile_path, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"New tab input fields saved to {filepath}")

        except Exception as e:
            print(f"Error scraping new tab inputs: {e}")

        return data

    def extract_questions_to_json(self):
        """Extracts all dynamic questions from the current questions page and saves them into JSON."""
        try:
            current_url = self.driver.current_url
            if "smartapply.indeed.com/beta/indeedapply/form/questions-module/questions" not in current_url:
                print(f"Not on a questions page. Current URL: {current_url}")
                return

            print(f"Extracting questions from: {current_url}")
            questions_data = {"url": current_url, "questions": []}

            # Locate all question blocks
            question_blocks = self.driver.find_elements(By.XPATH, "//div[contains(@data-testid,'input-')]")
            print(f"Found {len(question_blocks)} question blocks.")

            for idx, block in enumerate(question_blocks, start=1):
                try:
                    # Extract question label
                    label_elem = block.find_element(By.XPATH, ".//label")
                    question_text = label_elem.text.strip()

                    # Extract input details
                    input_elem = block.find_element(By.XPATH, ".//input | .//textarea | .//select")
                    input_type = input_elem.get_attribute("type") or "textarea/select"
                    input_name = input_elem.get_attribute("name")
                    placeholder = input_elem.get_attribute("placeholder")

                    questions_data["questions"].append({
                        "question_number": idx,
                        "question_text": question_text,
                        "input": {
                            "type": input_type,
                            "name": input_name,
                            "placeholder": placeholder
                        }
                    })
                except Exception as inner_err:
                    print(f"Could not extract question {idx}: {inner_err}")
                    continue

            # Save questions to JSON
            filename = "questions_latest.json"
            filepath = os.path.join(self.profile_path, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(questions_data, f, indent=4, ensure_ascii=False)

            print(f"Questions saved to {filepath}")

        except Exception as e:
            print(f"Error extracting questions: {e}")

    def _save_scraped_content_to_json(self):
        """Save page buttons to JSON for later use."""
        self.page_counter += 1
        filename = f"page_{self.page_counter}_contents.json"
        filepath = os.path.join(self.profile_path, filename)
        scraped_data = self.scrape_page_buttons()
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, indent=4, ensure_ascii=False)
            print(f"Page contents saved to {filepath}")
        except Exception as e:
            print(f"Error saving page contents to JSON: {e}")