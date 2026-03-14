# exploration/debug_linkedin_criteria.py
import requests
from bs4 import BeautifulSoup

url = "https://eg.linkedin.com/jobs/view/software-engineer-1-backend-at-noon-4375062284?position=1&pageNum=0&refId=RSduDusT%2FvogGUtspAe%2FSA%3D%3D&trackingId=wZh5t3nfskjNAdSg3H1FeA%3D%3D"  # أي URL من linkedin_full.json

res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(res.text, 'lxml')

print("All criteria:")
for c in soup.find_all('li', class_='description__job-criteria-item'):
    label = c.find('h3')
    value = c.find('span')
    if label and value:
        print(f"  '{label.get_text(strip=True)}' → '{value.get_text(strip=True)}'")