# find_selectors.py
from bs4 import BeautifulSoup

with open("real_rendered.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

# ── نلاقي الـ job cards ──
# بندور على links اللي فيها /jobs/p/ (دي صفحات الوظايف)
job_links = soup.find_all('a', href=lambda x: x and '/jobs/p/' in x)
print(f"✅ Found {len(job_links)} job links\n")

# شوف أول 3 وظايف وكل اللي حواليهم
for link in job_links[:3]:
    print("=" * 50)
    print("🔗 URL:", link.get('href'))
    print("📝 Title:", link.get_text(strip=True))
    
    # الـ parent div هو الـ card
    card = link.find_parent('div')
    if card:
        print("📦 Card HTML:")
        print(card.prettify()[:800])  # أول 800 حرف بس
    print()