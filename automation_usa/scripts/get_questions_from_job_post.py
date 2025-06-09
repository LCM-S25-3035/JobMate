from playwright.sync_api import sync_playwright

def get_questions(job_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(job_url)
        page.wait_for_timeout(5000)

        labels = page.locator("label").all_inner_texts()
        questions = [q for q in labels if "?" in q]
        browser.close()
        return questions
    
