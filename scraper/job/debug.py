# debug.py - شغل ده الأول
import requests
from fake_useragent import UserAgent

ua = UserAgent()
headers = {"User-Agent": ua.random}

url = "https://wuzzuf.net/jobs/egypt"
response = requests.get(url, headers=headers)

print("Status Code:", response.status_code)
print("Page Length:", len(response.text))

# احفظ الـ HTML عشان تشوفه
with open("debug_page.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Saved! Open debug_page.html in browser")