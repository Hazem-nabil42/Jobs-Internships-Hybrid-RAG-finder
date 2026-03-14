FROM python:3.12-slim

WORKDIR /app

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    wget gnupg && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

# Setup script - بيبني الـ DB لما الـ container يشتغل
RUN python database/vector_store.py || true
RUN python database/bm25_index.py || true

CMD ["uvicorn", "API.main:app", "--host", "0.0.0.0", "--port", "8000"]