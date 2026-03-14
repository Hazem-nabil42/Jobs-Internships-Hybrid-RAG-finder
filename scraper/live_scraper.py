# scraper/live_scraper.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import urllib.parse, time, json
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://wuzzuf.net"


# get details of a single job (used for live scraping)
def get_job_details_sync(url):
    """بيجيب تفاصيل وظيفة واحدة"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1500)

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page.content(), 'lxml')

            desc = soup.find('div', class_='css-1lqavbg')
            skills = soup.find('div', class_='css-14zw0ku')
            job_type = soup.find('a', class_='css-g65o95')
            work_style = soup.find('a', class_='css-wzyv7i')
            exp_spans = soup.find_all('span', class_='css-iu2m7n')

            browser.close()
            return {
                "description":  desc.get_text(separator='\n', strip=True) if desc else "N/A",
                "requirements": skills.get_text(separator='\n', strip=True) if skills else "N/A",
                "job_type":     job_type.get_text(strip=True) if job_type else "N/A",
                "work_style":   work_style.get_text(strip=True) if work_style else "N/A",
                "experience":   exp_spans[0].get_text(strip=True) if exp_spans else "N/A",
                "level":        exp_spans[1].get_text(strip=True) if len(exp_spans) > 1 else "N/A",
            }
    except Exception as e:
        print(f"❌ Details error: {e}")
        return {}


#scrape الوظايف من Wuzzuf بـ keyword معين
def _scrape_sync(query, num_pages=2):
    """بيشتغل في thread منفصل"""
    print(f"🌐 Live scraping: '{query}'...")
    encoded = urllib.parse.quote(query)
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for page_num in range(num_pages):
            url = f"{BASE_URL}/search/jobs/?q={encoded}&a=1&filters[country][0]=Egypt&start={page_num * 15}"
            page.goto(url)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)

            soup = BeautifulSoup(page.content(), 'lxml')
            job_links = soup.find_all('a', href=lambda x: x and '/jobs/p/' in x)

            for link in job_links:
                card = link.find_parent('div', class_=lambda x: x and 'css-lptxge' in x)
                if not card:
                    card = link.find_parent('div')
                if not card:
                    continue

                title = link.get_text(strip=True)
                job_url = BASE_URL + link['href'] if link['href'].startswith('/') else link['href']

                company_tag = card.find('a', class_=lambda x: x and 'css-ipsyv7' in x)
                company = company_tag.get_text(strip=True).replace(' -', '').strip() if company_tag else "N/A"

                location_tag = card.find('span', class_=lambda x: x and 'css-16x61xq' in x)
                location = location_tag.get_text(strip=True) if location_tag else "N/A"

                jobs.append({
                    "title":        title,
                    "url":          job_url,
                    "company":      company,
                    "location":     location,
                    "job_type":     "N/A",
                    "experience":   "N/A",
                    "level":        "N/A",
                    "description":  "N/A",
                    "requirements": "N/A",
                    "source":       "live"
                })
            time.sleep(1.5)
        browser.close()

    print(f"✅ Live found {len(jobs)} jobs")
    
    #details for each job
    print(f"📋 Getting details for {len(jobs)} jobs...")
    for job in jobs:
        details = get_job_details_sync(job['url'])
        job.update(details)
        time.sleep(1)

    return jobs


async def live_search_async(query, num_pages=2):
    """بيشغّل الـ sync scraper في thread pool عشان مش يبلوك الـ async loop"""
    import asyncio
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        jobs = await loop.run_in_executor(pool, _scrape_sync, query, num_pages)
    return jobs


def add_to_db(new_jobs):
    import chromadb
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    client = chromadb.PersistentClient(path="database/chroma_db")
    collection = client.get_collection("jobs")

    existing = collection.get()
    existing_urls = {m['url'] for m in existing['metadatas']} if existing['metadatas'] else set()
    truly_new = [j for j in new_jobs if j['url'] not in existing_urls]

    if not truly_new:
        print("ℹ️  All jobs already in DB")
        return

    print(f"➕ Adding {len(truly_new)} new jobs...")

    documents, metadatas, ids = [], [], []
    current_count = collection.count()

    for i, job in enumerate(truly_new):
        text = f"Title: {job.get('title','')} Company: {job.get('company','')} Location: {job.get('location','')}".strip()
        documents.append(text)
        metadatas.append({
            "title":      job.get("title", ""),
            "company":    job.get("company", ""),
            "location":   job.get("location", ""),
            "job_type":   job.get("job_type", "N/A"),
            "experience": job.get("experience", "N/A"),
            "level":      job.get("level", "N/A"),
            "url":        job.get("url", "")
        })
        ids.append(f"job_live_{current_count + i}")

    embeddings = model.encode(documents).tolist()
    collection.add(documents=documents, embeddings=embeddings,
                   metadatas=metadatas, ids=ids)

    json_path = "data/processed/wuzzuf_full.json"
    with open(json_path, "r", encoding="utf-8") as f:
        all_jobs = json.load(f)
    all_jobs.extend(truly_new)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)

    from database.bm25_index import build_bm25_index
    build_bm25_index()

    print(f"✅ DB updated! Total: {collection.count()} jobs")