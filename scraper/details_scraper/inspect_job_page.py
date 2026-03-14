# inspect_job_page.py
# inspect_job_page.py - الجزء الثاني
from bs4 import BeautifulSoup

with open("job_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

print("=" * 60)
print("✅ DESCRIPTION:")
desc = soup.find('div', class_='css-1lqavbg')
print(desc.get_text(separator='\n', strip=True) if desc else "NOT FOUND")

print("\n" + "=" * 60)
print("✅ SKILLS/REQUIREMENTS:")
skills = soup.find('div', class_='css-14zw0ku')
print(skills.get_text(separator='\n', strip=True) if skills else "NOT FOUND")

print("\n" + "=" * 60)
print("🔍 LOOKING FOR: job_type, experience, category...")

# بندور على الـ metadata (full time, years of experience, etc)
for tag in soup.find_all(['a', 'span', 'div'], class_=True):
    text = tag.get_text(strip=True)
    classes = " ".join(tag.get("class", []))
    keywords = ["Full Time", "Part Time", "Years", "Senior", "Junior", 
                "Mid", "Remote", "On-site", "Internship"]
    if any(kw.lower() in text.lower() for kw in keywords) and len(text) < 50:
        print(f"  Tag: <{tag.name}> | Class: {classes} | Text: {text}")