# scraper/job_details.py
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json, time, os

def get_job_details(page, url):
    try:
        page.goto(url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        soup = BeautifulSoup(page.content(), 'lxml')
        details = {}

        # ── Description ──
        desc = soup.find('div', class_='css-1lqavbg')
        details['description'] = desc.get_text(separator='\n', strip=True) if desc else "N/A"

        # ── Skills ──
        skills = soup.find('div', class_='css-14zw0ku')
        details['requirements'] = skills.get_text(separator='\n', strip=True) if skills else "N/A"

        # ── Job Type ──
        job_type = soup.find('a', class_='css-g65o95')
        details['job_type'] = job_type.get_text(strip=True) if job_type else "N/A"

        # ── Work Style (On-site / Remote) ──
        work_style = soup.find('a', class_='css-wzyv7i')
        details['work_style'] = work_style.get_text(strip=True) if work_style else "N/A"

        # ── Experience ──
        exp = soup.find('span', class_='css-iu2m7n')
        details['experience'] = exp.get_text(strip=True) if exp else "N/A"

        # ── Level (Junior / Senior) ──
        all_spans = soup.find_all('span', class_='css-iu2m7n')
        details['level'] = all_spans[1].get_text(strip=True) if len(all_spans) > 1 else "N/A"

        return details

    except Exception as e:
        print(f"    ❌ Error: {e}")
        return {}


def enrich_jobs():
    with open("data/raw/wuzzuf_jobs.json", "r", encoding="utf-8") as f:
        jobs = json.load(f)

    print(f"📋 Enriching {len(jobs)} jobs...\n")
    enriched = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for i, job in enumerate(jobs):
            print(f"[{i+1}/{len(jobs)}] {job['title']} @ {job['company']}")

            details = get_job_details(page, job['url'])
            full_job = {**job, **details}
            enriched.append(full_job)

            # preview أول وظيفة عشان نتأكد
            if i == 0:
                print("\n🔍 First job preview:")
                for k, v in full_job.items():
                    print(f"   {k}: {str(v)[:80]}")
                print()

            if (i + 1) % 10 == 0:
                with open("data/raw/wuzzuf_enriched_temp.json", "w", encoding="utf-8") as f:
                    json.dump(enriched, f, ensure_ascii=False, indent=2)
                print(f"   💾 Progress saved: {len(enriched)} jobs\n")

            time.sleep(1.5)

        browser.close()

    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/wuzzuf_full.json", "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 Done! Saved to data/processed/wuzzuf_full.json")


if __name__ == "__main__":
    enrich_jobs()