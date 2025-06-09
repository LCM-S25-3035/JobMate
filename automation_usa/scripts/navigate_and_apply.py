import time
from playwright.sync_api import sync_playwright

def apply_to_job(job_url, resume_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context()
        page = context.new_page()

        print(f"Navigating to: {job_url}")
        page.goto(job_url)
        time.sleep(6)

        try:
            apply_btn = page.locator('text="Apply Now"')
            if apply_btn.is_visible():
                print("Clicking 'Apply Now'...")
                apply_btn.click()
                time.sleep(3)

                print("Uploading resume...")
                page.set_input_files('input[type="file"]', resume_path)

                print("Submitting form...")
                page.click('button[type="submit"]')
            else:
                print("Apply button not visible.")

        except Exception as e:
            print(f"Error during apply: {e}")

        input("Press Enter to close browser after review...")
        browser.close()