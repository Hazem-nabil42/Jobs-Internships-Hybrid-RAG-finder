# scraper/base_scraper.py

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import json

class BaseScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
    
    def get_headers(self):
        """نتظاهر إننا browser عادي"""
        return {
            "User-Agent": self.ua.random,
            "Accept-Language": "en-US,en;q=0.9",
        }
    
    def fetch_page(self, url):
        """جلب صفحة مع error handling"""
        try:
            response = self.session.get(
                url, 
                headers=self.get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def polite_delay(self, min=1, max=3):
        """نستنى بين كل request عشان منتحجبش"""
        import random
        time.sleep(random.uniform(min, max))