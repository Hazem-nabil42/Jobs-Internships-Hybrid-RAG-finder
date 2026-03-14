# Jobs-Internships-Hybrid-RAG-finder
Jobs / Internships RAG system for Egyptian market

## متطلبات
- Python 3.10+
- Node.js (للـ Tailwind)

## تشغيل المشروع

### 1. Clone
git clone https://github.com/Hazem-nabil42/Jobs-Internships-Hybrid-RAG-finder.git
cd Jobs-Internships-Hybrid-RAG-finder

### 2. Setup (مرة واحدة بس)
python setup.py

### 3. Tailwind
npx tailwindcss -i ./src/css/input.css -o ./src/css/output.css

### 4. شغّل
uvicorn API.main:app --reload

### 5. افتح المتصفح
http://localhost:8000