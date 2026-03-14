# setup.py
import os, subprocess, sys

print("🚀 JIRAG Setup - جاري تجهيز المشروع...")
print("=" * 50)

# ── 1. Install requirements ──
print("\n📦 Installing requirements...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])

# ── 2. Create folders ──
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("database", exist_ok=True)

# ── 3. Check .env ──
if not os.path.exists(".env"):
    print("\n⚠️  مفيش .env file!")
    key = input("📝 حط الـ GROQ API KEY هنا: ").strip()
    with open(".env", "w") as f:
        f.write(f"GROQ_API_KEY={key}\n")
    print("✅ .env created!")

# ── 4. Scrape data ──
print("\n🕷️  Scraping jobs (هياخد ~20 دقيقة)...")
subprocess.run([sys.executable, "scraper/wuzzuf_scraper.py"])
subprocess.run([sys.executable, "scraper/job_details.py"])
subprocess.run([sys.executable, "scraper/linkedin_scraper.py"])
subprocess.run([sys.executable, "scraper/linkedin_details.py"])

# ── 5. Build DB ──
print("\n🗄️  Building Vector DB...")
subprocess.run([sys.executable, "database/vector_store.py"])
subprocess.run([sys.executable, "database/bm25_index.py"])

print("\n✅ Setup complete!")
print("🚀 شغّل: uvicorn API.main:app --reload")
print("🌐 افتح: http://localhost:8000")