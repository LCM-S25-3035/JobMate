import os
import json
import time
import undetected_chromedriver as uc

# Load config from JSON
with open("config.json", "r") as f:
    config = json.load(f)

driver_path = config["driver_path"]
profile_path = config["profile_path"]
indeed_url = config["indeed_url"]

# Ensure profile folder exists
os.makedirs(profile_path, exist_ok=True)

# Launch Chrome with undetected_chromedriver
driver = uc.Chrome(
    driver_executable_path=driver_path,
    user_data_dir=profile_path,
    headless=False
)

# Navigate to Indeed login page
driver.get(indeed_url)

print("Please log in manually in the browser. This session will be saved in your JobMateChrome profile.")
input("Press Enter once you're done logging in...")

driver.quit()
