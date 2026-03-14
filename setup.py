"""
JIRAG — Setup Script
Run this once to install dependencies, scrape jobs, and build the database.
"""

import os
import subprocess
import sys


def run(cmd):
    """Run a command and print output in real time."""
    subprocess.run(cmd, check=True)


def create_folders():
    """Create required project directories."""
    folders = ["data/raw", "data/processed", "database"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    print("✅ Folders created")


def setup_env():
    """Create .env file if it doesn't exist."""
    if os.path.exists(".env"):
        print("✅ .env already exists")
        return

    print("\n⚠️  No .env file found!")
    key = input("Enter your GROQ API KEY: ").strip()
    with open(".env", "w") as f:
        f.write(f"GROQ_API_KEY={key}\n")
    print("✅ .env created")


def install_python_deps():
    """Install Python dependencies from requirements.txt."""
    print("\n📦 Installing Python dependencies...")
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Python dependencies installed")


def install_playwright():
    """Install Playwright browser (Chromium) for scraping."""
    print("\n🌐 Installing Playwright browser...")
    run([sys.executable, "-m", "playwright", "install", "chromium"])
    print("✅ Playwright installed")


def install_node_deps():
    """
    Install Node.js dependencies for Tailwind CSS.
    Requires Node.js to be installed on the machine.
    Run: npm install
    Then to build CSS: npx tailwindcss -i ./src/css/input.css -o ./src/css/output.css
    """
    if not os.path.exists("package.json"):
        print("⚠️  No package.json found — skipping npm install")
        return

    print("\n🎨 Installing Node.js dependencies (Tailwind)...")
    run(["npm", "install"])
    print("✅ Node dependencies installed")

    # Build Tailwind CSS output
    print("🎨 Building Tailwind CSS...")
    run(["npx", "tailwindcss",
         "-i", "./src/css/input.css",
         "-o", "./src/css/output.css"])
    print("✅ Tailwind CSS built")


def scrape_jobs():
    """Scrape jobs from Wuzzuf and LinkedIn."""
    print("\n🕷️  Scraping Wuzzuf jobs (~15 min)...")
    run([sys.executable, "scraper/wuzzuf_scraper.py"])

    print("\n🕷️  Fetching Wuzzuf job details (~20 min)...")
    run([sys.executable, "scraper/details_scraper/wazzuf_details.py"])

    print("\n🔗 Scraping LinkedIn jobs (~10 min)...")
    run([sys.executable, "scraper/linkedin_scraper.py"])

    print("\n🔗 Fetching LinkedIn job details (~10 min)...")
    run([sys.executable, "scraper/details_scraper/linkedin_details.py"])

    print("✅ Scraping complete")


def build_database():
    """Build Vector DB and BM25 index from scraped data."""
    print("\n🗄️  Building Vector Database...")
    run([sys.executable, "database/vector_store.py"])

    print("\n📊 Building BM25 Index...")
    run([sys.executable, "database/bm25_index.py"])

    print("✅ Database ready")


def main():
    print("=" * 50)
    print("  JIRAG — AI Jobs Finder for Egyptian Market")
    print("  Setup Script")
    print("=" * 50)

    create_folders()
    setup_env()
    install_python_deps()
    install_playwright()
    install_node_deps()
    scrape_jobs()
    build_database()

    print("\n" + "=" * 50)
    print("✅ Setup complete! Ready to run.")
    print("")
    print("  Start the server:")
    print("  uvicorn API.main:app --reload")
    print("")
    print("  Open in browser:")
    print("  http://localhost:8000")
    print("=" * 50)


if __name__ == "__main__":
    main()
