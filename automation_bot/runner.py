import os
import json
from sites.indeed import IndeedBot
from sites.glassdoor import GlassdoorBot

# Get the directory where the current Python file is
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "config.json")

def main():
    # Load config.json and set as environment variables
    with open(config_path, "r") as f:
        config = json.load(f)

    for key, value in config.items():
        os.environ[key.upper()] = str(value)

    driver_path = os.environ["DRIVER_PATH"]
    profile_path = os.environ["PROFILE_PATH"]

    # Choose site dynamically
    site = os.environ.get("SITE", "glassdoor").lower()

    if site == "glassdoor":
        bot = GlassdoorBot(driver_path, profile_path)
        bot.run()
        bot.browser.quit()
    elif site == "indeed":
        bot = IndeedBot(driver_path, profile_path)
        bot.login()
        bot.quit()

if __name__ == "__main__":
    main()