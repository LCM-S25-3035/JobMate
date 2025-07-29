from selenium.webdriver.common.by import By

class CaptchaHandler:
    def __init__(self, driver):
        self.driver = driver

    def _wait_for_captcha(self):
        """
        Checks for a reCAPTCHA and waits for the user to solve it if present.
        Only prompts if the reCAPTCHA is visible and active.
        """
        print("Checking for reCAPTCHA...")
        try:
            captcha_found = False
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute("src")
                if src and "recaptcha" in src.lower():
                    # Switch into the iframe to check for active captcha
                    self.driver.switch_to.frame(iframe)
                    try:
                        captcha_checkbox = self.driver.find_element(By.ID, "recaptcha-anchor")
                        if captcha_checkbox.is_displayed():
                            captcha_found = True
                            print("Active reCAPTCHA detected! Please solve it manually in the browser.")
                            input("Press Enter here once you've solved the reCAPTCHA to continue...")
                            break
                    except Exception as e:
                        print(f"Error inside captcha iframe: {e}")
                    finally:
                        self.driver.switch_to.default_content()

            if not captcha_found:
                print("No active reCAPTCHA found on this page.")
        except Exception as e:
            print(f"Error checking for reCAPTCHA: {e}")
