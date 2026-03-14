# scraper/linkedin_scraper.py - النسخة الكاملة
import requests
from bs4 import BeautifulSoup
import json, time, os

SEARCH_QUERIES = [
    # Tech
    "software engineer egypt",
    "python developer egypt",
    "data scientist egypt",
    "machine learning egypt",
    "frontend developer egypt",
    "backend developer egypt",
    "flutter developer egypt",
    "devops egypt",
    "cybersecurity egypt",
    "product manager egypt",
    "data analyst egypt",
    "AI engineer egypt",

    # Business
    "marketing egypt",
    "sales egypt",
    "customer service egypt",
    "business development egypt",
    "digital marketing egypt",

    # Fresh Grads
    "fresh graduate egypt",
    "internship egypt",
    "entry level egypt",

    # Remote
    "remote egypt",
    "work from home egypt",
]

def scrape_linkedin_query(query, num_pages=5):
    jobs = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "trk": "guest_homepage-basic_guest_nav_menu_jobs"
    }

    for page in range(num_pages):
        url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        params = {
            "keywords": query,
            "location": "Egypt",
            "start": page * 25
        }

        try:
            res = requests.get(url, headers=headers, params=params, timeout=10)
            if res.status_code != 200:
                print(f"  ⚠️ Status {res.status_code} — stopping")
                break

            soup = BeautifulSoup(res.text, 'lxml')
            cards = soup.find_all('li')

            for card in cards:
                title_tag    = card.find('h3', class_='base-search-card__title')
                company_tag  = card.find('h4', class_='base-search-card__subtitle')
                location_tag = card.find('span', class_='job-search-card__location')
                link_tag     = card.find('a', class_='base-card__full-link')
                time_tag     = card.find('time')

                if not title_tag:
                    continue

                jobs.append({
                    "title":       title_tag.get_text(strip=True),
                    "company":     company_tag.get_text(strip=True) if company_tag else "N/A",
                    "location":    location_tag.get_text(strip=True) if location_tag else "N/A",
                    "url":         link_tag['href'] if link_tag else "N/A",
                    "posted":      time_tag.get_text(strip=True) if time_tag else "N/A",
                    "job_type":    "N/A",
                    "experience":  "N/A",
                    "level":       "N/A",
                    "description": "N/A",
                    "source":      "linkedin"
                })

            print(f"  📄 [{query}] Page {page+1}: {len(cards)} jobs")
            time.sleep(2)  # مهم عشان منتحجبش

        except Exception as e:
            print(f"  ❌ Error: {e}")
            break

    return jobs


def scrape_all_linkedin(num_pages=3):
    all_jobs = []
    seen_urls = set()

    for query in SEARCH_QUERIES:
        print(f"\n🔍 Scraping: '{query}'")
        jobs = scrape_linkedin_query(query, num_pages)

        for job in jobs:
            if job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                all_jobs.append(job)

        print(f"  ✅ Unique so far: {len(all_jobs)}")
        time.sleep(3)  # delay بين كل query

    return all_jobs


if __name__ == "__main__":
    jobs = scrape_all_linkedin(num_pages=3)

    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/linkedin_jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 Total LinkedIn jobs: {len(jobs)}")
    print("📁 Saved to data/raw/linkedin_jobs.json")