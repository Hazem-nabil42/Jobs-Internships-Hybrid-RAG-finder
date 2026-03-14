# database/hybrid_retriever.py - استبدل الملف كله

import chromadb
import pickle
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
client = chromadb.PersistentClient(path="database/chroma_db")
collection = client.get_collection("jobs")

with open("database/bm25_index.pkl", "rb") as f:
    data = pickle.load(f)
    bm25 = data["bm25"]
    jobs = data["jobs"]


def hybrid_search(query, n_results=15):
    print(f"\n🔍 Query: '{query}'")
    print("=" * 50)

    # ── 1. BM25 Search → رتّب كل الوظايف ──
    query_words = query.lower().split()
    bm25_scores = bm25.get_scores(query_words)
    
    # رتّب من الأعلى للأقل وخد أحسن 20
    bm25_ranked = sorted(range(len(bm25_scores)), 
                         key=lambda i: bm25_scores[i], 
                         reverse=True)[:20]

    # ── 2. Vector Search → أحسن 20 ──
    query_vector = model.encode(query).tolist()
    vector_results = collection.query(
        query_embeddings=[query_vector],
        n_results=20
    )
    vector_urls = [m['url'] for m in vector_results['metadatas'][0]]

    # ── 3. RRF - Reciprocal Rank Fusion ──
    # الفكرة: كل وظيفة بتاخد score بناءً على رتبتها مش score مطلق
    # score = 1/(k + rank) حيث k=60
    # مثلاً: rank 1 → 1/61 = 0.016, rank 5 → 1/65 = 0.015
    
    K = 60
    rrf_scores = {}

    # BM25 ranks
    for rank, job_idx in enumerate(bm25_ranked):
        url = jobs[job_idx]['url']
        rrf_scores[url] = rrf_scores.get(url, 0) + 1 / (K + rank + 1)

    # Vector ranks
    for rank, url in enumerate(vector_urls):
        rrf_scores[url] = rrf_scores.get(url, 0) + 1 / (K + rank + 1)

    # ── 4. Sort وشيل المكرر ──
    seen_titles = set()
    top_results = []

    for url in sorted(rrf_scores, key=rrf_scores.get, reverse=True):
        job = next((j for j in jobs if j['url'] == url), None)
        if not job:
            continue

        title_key = job['title'].lower().strip()
        if title_key in seen_titles:
            continue

        seen_titles.add(title_key)
        top_results.append({
            "job": job,
            "score": round(rrf_scores[url], 4)
        })

        if len(top_results) == n_results:
            break

    # ── 5. اعرض النتايج ──
    for i, r in enumerate(top_results):
        job = r['job']
        print(f"\n#{i+1} (score: {r['score']})")
        print(f"  Title:      {job['title']}")
        print(f"  Company:    {job['company']}")
        print(f"  Location:   {job['location']}")
        print(f"  Experience: {job.get('experience', 'N/A')}")
        print(f"  Level:      {job.get('level', 'N/A')}")
        print(f"  Job Type:   {job.get('job_type', 'N/A')}")
        source = job.get('source', 'wuzzuf')
        print(f"  Source:     {source}")

    return top_results


if __name__ == "__main__":
    hybrid_search("python developer cairo")
    hybrid_search("customer service english fresh grad")
    hybrid_search("data scientist machine learning")

## ليه RRF أحسن؟
# ```
# Weighted Sum (القديم):
#   BM25 score:   7.482 normalized → 1.0
#   Vector score: 0.9 (عالي غلط)
#   Final = 0.8×1.0 + 0.2×0.9 = 0.98 ← ممكن يتخطى

# RRF (الجديد):
#   BM25 rank 1:   1/(60+1) = 0.0164
#   Vector rank 1: 1/(60+1) = 0.0164
#   Total = 0.0328

#   لو وظيفة في BM25 rank 1 وفي Vector rank 10:
#   = 1/61 + 1/70 = 0.0164 + 0.0143 = 0.0307 ✅ أعلى من حاجة rank 5 في الاتنين