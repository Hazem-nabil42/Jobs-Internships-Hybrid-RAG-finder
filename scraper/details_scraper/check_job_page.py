# check_job_page.py
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# خد أول وظيفة من الـ JSON
import json
with open("data/raw/wuzzuf_jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

first_job_url = jobs[0]['url']
print("Checking:", first_job_url)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    page.goto(first_job_url)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    # احفظ الـ HTML
    html = page.content()
    with open("job_page.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("Saved job_page.html")
    print("Length:", len(html))
    
    input("Press Enter to close...")
    browser.close()