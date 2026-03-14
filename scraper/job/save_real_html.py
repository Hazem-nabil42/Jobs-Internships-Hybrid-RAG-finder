# save_real_html.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # ✅ الـ URL الصح - صفحة search عامة
    page.goto("https://wuzzuf.net/search/jobs/?q=&a=1&filters[country][0]=Egypt")
    
    # استنى الصفحة تخلص تماماً
    page.wait_for_load_state("networkidle")
    
    # استنى 3 ثواني زيادة عشان الـ JS
    page.wait_for_timeout(3000)
    
    # شوف إيه الموجود فعلاً
    html = page.content()
    
    # ── دور على أي links فيها كلمة jobs ──
    links = page.query_selector_all('a[href*="/jobs/"]')
    print(f"Job links found: {len(links)}")
    
    if links:
        for link in links[:3]:
            print(" →", link.inner_text()[:50], "|", link.get_attribute("href"))
    
    # احفظ الـ HTML
    with open("real_rendered.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"\nHTML Length: {len(html)}")
    print("✅ Saved! Now check real_rendered.html")
    
    input("Press Enter to close browser...")  # خليه مفتوح عشان تشوف
    browser.close()