#!/usr/bin/env python3
"""
End-to-End Test for One-Click Application Feature

This script tests the entire flow of:
1. Finding a job
2. Uploading a resume
3. Getting a tailored resume and cover letter
4. Using the one-click application button to apply

Usage:
python test_e2e_application.py
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def setup_driver():
    """Set up the Chrome driver with headless option"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode, comment out for debugging
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login(driver, base_url, email, password):
    """Login to the application"""
    logger.info("Logging in...")
    driver.get(f"{base_url}/auth/login")
    
    # Wait for the login form to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    
    # Enter credentials
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    
    # Submit the form
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    # Wait for redirect to complete
    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )
    
    logger.info("Login successful")

def find_job_with_email(driver, base_url):
    """Find a job with an email application method"""
    logger.info("Finding a job with email application...")
    driver.get(f"{base_url}/jobs/mongo")
    
    # Wait for jobs to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "job-card"))
    )
    
    # Find a job with email application (look for mail icon)
    job_cards = driver.find_elements(By.CLASS_NAME, "job-card")
    for i, card in enumerate(job_cards):
        if card.find_elements(By.CSS_SELECTOR, "i.fa-envelope"):
            logger.info(f"Found job with email application: {i+1}")
            job_title = card.find_element(By.CSS_SELECTOR, "h5").text
            tailor_link = card.find_element(By.LINK_TEXT, "Tailor Resume")
            
            # Store job ID from URL
            job_id = tailor_link.get_attribute("href").split("/")[-1]
            logger.info(f"Job ID: {job_id}, Title: {job_title}")
            
            tailor_link.click()
            return job_id
    
    logger.error("No job with email application found")
    return None

def upload_resume(driver, resume_path):
    """Upload a resume for tailoring"""
    logger.info("Uploading resume...")
    
    # Wait for file input to be present
    file_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "resume_file"))
    )
    
    # Upload file
    file_input.send_keys(resume_path)
    
    # Submit form
    driver.find_element(By.XPATH, "//button[contains(text(), 'Tailor Resume')]").click()
    
    # Wait for tailoring to complete (look for tabs navigation)
    WebDriverWait(driver, 60).until(  # Longer timeout as AI processing takes time
        EC.presence_of_element_located((By.ID, "resultTabs"))
    )
    
    logger.info("Resume upload and tailoring successful")

def send_one_click_application(driver):
    """Test the one-click application button"""
    logger.info("Testing one-click application...")
    
    # Wait for apply tab (need to click it first)
    apply_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "apply-tab"))
    )
    apply_tab.click()
    
    # Wait for the tab content to be visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "apply"))
    )
    
    # Find and click the one-click application button
    one_click_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "send-application-btn"))
    )
    one_click_button.click()
    
    # Wait for success message
    success_message = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "application-status"))
    )
    
    # Check if application was successful
    if "success" in success_message.text.lower():
        logger.info("One-click application successful")
        return True
    else:
        logger.error(f"One-click application failed: {success_message.text}")
        return False

def main():
    """Main function to run the E2E test"""
    parser = argparse.ArgumentParser(description='Run end-to-end test for one-click application')
    parser.add_argument('--base-url', default='http://localhost:5002', help='Base URL of the application')
    parser.add_argument('--email', default='test@example.com', help='Login email')
    parser.add_argument('--password', default='password', help='Login password')
    parser.add_argument('--resume', default='test_resume_sample.txt', help='Path to resume file')
    
    args = parser.parse_args()
    
    driver = setup_driver()
    
    try:
        # Step 1: Login
        login(driver, args.base_url, args.email, args.password)
        
        # Step 2: Find a job with email application
        job_id = find_job_with_email(driver, args.base_url)
        if not job_id:
            raise Exception("Could not find a suitable job for testing")
        
        # Step 3: Upload resume and get tailored version
        upload_resume(driver, os.path.abspath(args.resume))
        
        # Step 4: Send one-click application
        result = send_one_click_application(driver)
        
        if result:
            logger.info("E2E TEST PASSED ✅")
        else:
            logger.error("E2E TEST FAILED ❌")
            
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
    finally:
        # Take screenshot before closing
        driver.save_screenshot("e2e_test_result.png")
        logger.info("Screenshot saved as e2e_test_result.png")
        
        driver.quit()

if __name__ == "__main__":
    main()
