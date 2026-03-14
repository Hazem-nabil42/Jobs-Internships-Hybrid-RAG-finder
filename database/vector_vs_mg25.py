# debug_search.py - أضف ده
import pickle
from rank_bm25 import BM25Okapi

with open("database/bm25_index.pkl", "rb") as f:
    data = pickle.load(f)
    bm25 = data["bm25"]
    jobs = data["jobs"]

query_words = "python developer cairo".split()
scores = bm25.get_scores(query_words)

# شوف الـ score بتاع الـ python jobs بالظبط
print("BM25 scores for python jobs:")
for i, job in enumerate(jobs):
    if "python" in job.get("title", "").lower():
        print(f"  Score: {scores[i]:.3f} | {job['title']}")

print("\nTop 5 BM25 overall:")
top5 = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:5]
for i in top5:
    print(f"  Score: {scores[i]:.3f} | {jobs[i]['title']}")