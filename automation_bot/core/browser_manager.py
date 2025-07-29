import os
import shutil
import time
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options

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
        
        # Load proxy configuration from config.json
        self.proxy_config = self._load_proxy_config()
        
        # Load window positioning configuration
        self.window_config = self._load_window_config()

        # Clone original profile if needed
        if self.use_temp_profile:
            self._clone_profile_to_temp()

        # Launch browser
        self.driver = self._launch_browser()

    def _load_proxy_config(self):
        """Load proxy configuration from config.json"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('proxy', {})
        except Exception as e:
            print(f"Could not load proxy config: {e}")
            return {}

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
            # Set up Chrome options
            options = Options()
            
            # Configure proxy if enabled
            if self.proxy_config.get('enabled', False):
                proxy_host = self.proxy_config.get('host')
                proxy_port = self.proxy_config.get('port')
                proxy_username = self.proxy_config.get('username')
                proxy_password = self.proxy_config.get('password')
                
                if proxy_host and proxy_port:
                    proxy_server = f"{proxy_host}:{proxy_port}"
                    print(f"Configuring Bright Data proxy: {proxy_server}")
                    
                    # Add proxy configuration
                    options.add_argument(f'--proxy-server=http://{proxy_server}')
                    
                    # If authentication is required, we'll need to handle it differently
                    if proxy_username and proxy_password:
                        print("Proxy authentication configured")
                        # Chrome extension method for proxy auth will be added below
                        self._setup_proxy_auth(options, proxy_username, proxy_password, proxy_host, proxy_port)
                else:
                    print("Proxy enabled but host/port not configured properly")
            else:
                print("Proxy disabled or not configured")

            driver = uc.Chrome(
                user_data_dir=self.profile_path,
                headless=False,  # Keep browser visible for login
                options=options
            )
            
            # Position browser window for side-by-side viewing
            self._position_browser_window(driver)
            
            print("Browser launched successfully.")
            return driver
        except Exception as e:
            print(f"Error launching Undetected ChromeDriver: {e}")
            raise

    def _setup_proxy_auth(self, options, username, password, host, port):
        """Set up proxy authentication using Chrome extension"""
        import zipfile
        import tempfile
        
        try:
            # Create a temporary directory for the proxy auth extension
            extension_dir = tempfile.mkdtemp()
            
            # Create manifest.json for the extension
            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Bright Data Proxy Auth",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """
            
            # Create background.js for the extension
            background_js = f"""
            var config = {{
                mode: "fixed_servers",
                rules: {{
                    singleProxy: {{
                        scheme: "http",
                        host: "{host}",
                        port: parseInt({port})
                    }},
                    bypassList: ["localhost"]
                }}
            }};

            chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

            function callbackFn(details) {{
                return {{
                    authCredentials: {{
                        username: "{username}",
                        password: "{password}"
                    }}
                }};
            }}

            chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {{urls: ["<all_urls>"]}},
                ['blocking']
            );
            """
            
            # Write files to extension directory
            with open(os.path.join(extension_dir, 'manifest.json'), 'w') as f:
                f.write(manifest_json)
            
            with open(os.path.join(extension_dir, 'background.js'), 'w') as f:
                f.write(background_js)
            
            # Add the extension to Chrome options
            options.add_argument(f'--load-extension={extension_dir}')
            print(f"Proxy authentication extension created at: {extension_dir}")
            
        except Exception as e:
            print(f"Error setting up proxy authentication: {e}")
            # Fallback to basic proxy without auth

    def _load_window_config(self):
        """Load window positioning configuration from config.json"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('window_positioning', {})
        except Exception as e:
            print(f"Could not load window config: {e}")
            return {}

    def _position_browser_window(self, driver):
        """Position browser window for side-by-side viewing"""
        try:
            # Check if window positioning is enabled
            if not self.window_config.get('enabled', False):
                print("Window positioning disabled")
                return
                
            import time
            time.sleep(2)  # Wait for browser to fully load
            
            # Get screen resolution
            screen_width = driver.execute_script("return screen.width;")
            screen_height = driver.execute_script("return screen.height;")
            
            # Get configuration
            position = self.window_config.get('position', 'left')  # 'left' or 'right'
            width_percentage = self.window_config.get('width_percentage', 50)  # Default 50%
            
            # Calculate window dimensions
            window_width = int(screen_width * (width_percentage / 100))
            window_height = screen_height - 100  # Leave space for taskbar
            
            # Calculate position
            if position.lower() == 'right':
                x_position = screen_width - window_width  # Right side
            else:
                x_position = 0  # Left side (default)
            
            y_position = 0  # Top
            
            # Set window size and position
            driver.set_window_size(window_width, window_height)
            driver.set_window_position(x_position, y_position)
            
            print(f"Browser positioned: {window_width}x{window_height} at ({x_position}, {y_position}) - {position} side")
            
        except Exception as e:
            print(f"Could not position browser window: {e}")
            # Continue without positioning

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
                time.sleep(0.5)  # Reduced from 1 to 0.5 seconds - Let UI settle
                self.scroll_into_view(element)

            element.click()
            print("Clicked element successfully.")

        except ElementClickInterceptedException:
            print("Click intercepted. Retrying after dismissing modals...")
            if site_modal_handler:
                site_modal_handler()
            self.handle_generic_popups()
            time.sleep(0.5)  # Reduced timing - Let UI settle
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
                        time.sleep(1)  # Reduced from 2 to 1 second
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
                except Exception:
                    continue
            # Example: Modal close buttons
            close_btns = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Close') or @aria-label='Close']")
            for btn in close_btns:
                try:
                    self.click_element(btn)
                    print("Closed modal popup.")
                    return True
                except Exception:
                    continue
            print("No generic popups detected.")
            return False
        except Exception as e:
            print(f"Error handling popups: {e}")
            return False



