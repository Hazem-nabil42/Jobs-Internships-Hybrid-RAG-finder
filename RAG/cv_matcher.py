# rag/cv_matcher.py - النسخة الصح

import fitz
import chromadb
import math
from sentence_transformers import SentenceTransformer
from groq import Groq
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
client = chromadb.PersistentClient(path="database/chroma_db")
collection = client.get_collection("jobs")


def extract_text_from_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()


def extract_skills_from_cv(cv_text):
    """
    بنستخدم LLM عشان يستخرج المهارات والخبرة من الـ CV
    بدل ما نبعت الـ CV كامل للـ embedding
    """
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""من الـ CV ده، استخرج:
1. المسمى الوظيفي المناسب
2. المهارات التقنية
3. سنوات الخبرة
4. المجال

رد بالإنجليزي فقط في صيغة:
Job Title: ...
Skills: skill1, skill2, skill3, ...
Experience: X years
Field: ...

CV:
{cv_text[:3000]}"""
        }],
        max_tokens=200
    )

    extracted = response.choices[0].message.content
    print(f"📋 Extracted profile:\n{extracted}\n")
    return extracted


def distance_to_score(distance):
    return round(math.exp(-distance / 10) * 100, 1)


def match_cv_to_jobs(pdf_bytes, n_results=5):
    # ── 1. استخرج النص ──
    cv_text = extract_text_from_pdf(pdf_bytes)
    if not cv_text:
        return [], "مش قادر أقرأ الـ CV"

    print(f"📄 CV text: {len(cv_text)} chars")

    # ── 2. استخرج الـ skills بالـ LLM ──
    skills_profile = extract_skills_from_cv(cv_text)

    # ── 3. حول الـ profile للـ vector (مش الـ CV كامل) ──
    cv_vector = model.encode(skills_profile).tolist()

    # ── 4. دور في الـ DB ──
    results = collection.query(
        query_embeddings=[cv_vector],
        n_results=n_results
    )

    distances = results['distances'][0]
    print(f"Raw distances: {[round(d,2) for d in distances]}")

    # ── 5. احسب الـ scores ──
    matches = []
    for i, metadata in enumerate(results['metadatas'][0]):
        matches.append({
            "title":      metadata.get("title", "N/A"),
            "company":    metadata.get("company", "N/A"),
            "location":   metadata.get("location", "N/A"),
            "experience": metadata.get("experience", "N/A"),
            "level":      metadata.get("level", "N/A"),
            "job_type":   metadata.get("job_type", "N/A"),
            "url":        metadata.get("url", "#"),
            "source":     metadata.get("source", "wuzzuf"),
            "match":      distance_to_score(distances[i])
        })

    # ── 6. normalize الـ scores بين 60% و 99% ──
    # عشان الـ scores تبان منطقية للمستخدم
    if matches:
        max_score = max(m['match'] for m in matches)
        min_score = min(m['match'] for m in matches)

        for m in matches:
            if max_score != min_score:
                normalized = 60 + ((m['match'] - min_score) / (max_score - min_score)) * 39
                m['match'] = round(normalized, 1)
            else:
                m['match'] = 75.0

    matches.sort(key=lambda x: x['match'], reverse=True)
    return matches, skills_profile


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "rb") as f:
            pdf_bytes = f.read()

        matches, profile = match_cv_to_jobs(pdf_bytes)
        print(f"\n🎯 Top matches:")
        for m in matches:
            print(f"  {m['match']}% | {m['title']} @ {m['company']}")