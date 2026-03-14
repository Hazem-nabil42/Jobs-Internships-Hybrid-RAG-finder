# database/bm25_index.py
from rank_bm25 import BM25Okapi
import json, pickle, os

def build_bm25_index():
    # ── لود Wuzzuf ──
    with open("data/processed/wuzzuf_full.json", "r", encoding="utf-8") as f:
        wuzzuf_jobs = json.load(f)

    # ── لود LinkedIn ──
    linkedin_path = "data/processed/linkedin_full.json"
    linkedin_jobs = []
    if os.path.exists(linkedin_path):
        with open(linkedin_path, "r", encoding="utf-8") as f:
            linkedin_jobs = json.load(f)

    # ── دمج الكل ──
    all_jobs = wuzzuf_jobs + linkedin_jobs
    print(f"📋 Building BM25 index for {len(all_jobs)} jobs...")
    print(f"   Wuzzuf:   {len(wuzzuf_jobs)}")
    print(f"   LinkedIn: {len(linkedin_jobs)}")

    corpus = []
    for job in all_jobs:
        text = f"""
        {job.get('title', '')}
        {job.get('company', '')}
        {job.get('description', '')}
        {job.get('requirements', '')}
        {job.get('job_type', '')}
        {job.get('experience', '')}
        {job.get('level', '')}
        """.lower()

        corpus.append(text.split())

    bm25 = BM25Okapi(corpus)

    os.makedirs("database", exist_ok=True)
    with open("database/bm25_index.pkl", "wb") as f:
        pickle.dump({"bm25": bm25, "jobs": all_jobs}, f)

    print(f"✅ BM25 index built! Total: {len(all_jobs)} jobs")

    # Quick test
    print("\n🔍 Quick test: 'python developer'")
    scores = bm25.get_scores("python developer".split())
    top_3 = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]
    for i in top_3:
        source = all_jobs[i].get('source', 'wuzzuf')
        print(f"  [{source}] {all_jobs[i]['title']} @ {all_jobs[i]['company']} (score: {scores[i]:.2f})")


if __name__ == "__main__":
    build_bm25_index()