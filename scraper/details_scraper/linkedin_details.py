# scraper/linkedin_details.py
import requests
from bs4 import BeautifulSoup
import json, time, os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_linkedin_details(url):
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return {}

        soup = BeautifulSoup(res.text, 'lxml')

        desc = soup.find('div', class_='description__text')
        description = desc.get_text(separator='\n', strip=True) if desc else "N/A"

        details = {
            "description": description,
            "job_type":    "N/A",
            "level":       "N/A",
            "experience":  "N/A",
            "category":    "N/A",
        }

        criteria = soup.find_all('li', class_='description__job-criteria-item')
        for c in criteria:
            label = c.find('h3')
            value = c.find('span')
            if not label or not value:
                continue

            label_text = label.get_text(strip=True)
            value_text = value.get_text(strip=True)

            if 'أقدمية' in label_text:
                details['level'] = value_text
            elif 'توظيف' in label_text:
                details['job_type'] = value_text
            elif 'مهام' in label_text:
                details['category'] = value_text

        # ── اشتق الـ experience من الـ level ──
        level_to_exp = {
            'مستوى المبتدئين':        '0 to 2 years',
            'مستوى متوسط الأقدمية':   '2 to 5 years',
            'مستوى أقدمية متوسطة':    '2 to 5 years',
            'مستوى متوسط':            '2 to 5 years',
            'مستوى الأقدمية العليا':  '5 to 10 years',
            'مستوى مدير':             '5+ years',
            'مستوى المدير':           '5+ years',
            'غير مطبق':               'Not specified',  # ← أضف ده
            'لا ينطبق':               'Not specified',  # ← وده
        }
        details['experience'] = level_to_exp.get(details['level'], 'N/A')

        return details

    except Exception as e:
        print(f"    ❌ Error: {e}")
        return {}



def enrich_linkedin_jobs():
    with open("data/raw/linkedin_jobs.json", "r", encoding="utf-8") as f:
        jobs = json.load(f)

    print(f"📋 Enriching {len(jobs)} LinkedIn jobs...\n")
    enriched = []

    for i, job in enumerate(jobs):
        print(f"[{i+1}/{len(jobs)}] {job['title']} @ {job['company']}")

        if job.get('url', 'N/A') == 'N/A':
            enriched.append(job)
            continue

        details = get_linkedin_details(job['url'])
        full_job = {**job, **details}
        enriched.append(full_job)

        # preview أول وظيفة
        if i == 0:
            print("\n🔍 First job preview:")
            for k, v in full_job.items():
                print(f"   {k}: {str(v)[:80]}")
            print()

        # save كل 10
        if (i + 1) % 10 == 0:
            with open("data/raw/linkedin_enriched_temp.json", "w", encoding="utf-8") as f:
                json.dump(enriched, f, ensure_ascii=False, indent=2)
            print(f"   💾 Progress: {len(enriched)} jobs\n")

        time.sleep(1.5)  # مهم

    # save final
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/linkedin_full.json", "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 Done! Saved to data/processed/linkedin_full.json")


if __name__ == "__main__":
    enrich_linkedin_jobs()