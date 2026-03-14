# rag/pipeline.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groq import Groq
from database.hybrid_retriever import hybrid_search
from dotenv import load_dotenv
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

#LIVE_SCRAPE_THRESHOLD = 0.028  # لو أعلى score أقل من ده → live scrape


def format_jobs_for_llm(results):
    """بنحول الوظايف لنص مفهوم للـ LLM"""
    if not results:
        return "مفيش وظايف متاحة دلوقتي."
    
    text = ""
    for i, r in enumerate(results):
        job = r['job']
        text += f"""
        وظيفة #{i+1}:
        - الاسم: {job.get('title', 'N/A')}
        - الشركة: {job.get('company', 'N/A')}
        - الموقع: {job.get('location', 'N/A')}
        - النوع: {job.get('job_type', 'N/A')}
        - الخبرة المطلوبة: {job.get('experience', 'N/A')}
        - المستوى: {job.get('level', 'N/A')}
        - الوصف: {job.get('description', 'N/A')[:200]}
        - الرابط: {job.get('url', 'N/A')}
        ---"""
    return text

# is the results relevant enough to the query? (based on keyword matching)
def results_are_relevant(query, results, min_keyword_match=0.5):
    if not results:
        return False

    query_words = set(query.lower().split())
    query_words = {w for w in query_words if len(w) > 3}  # شيل كلمات أقل من 4 حروف

    print(f"🔍 Checking keywords: {query_words}")

    matched = 0
    for r in results[:3]:
        job = r['job']
        # ← title بس مش description
        job_title = job.get('title', '').lower()

        for word in query_words:
            if word in job_title:
                matched += 1
                print(f"  ✅ '{word}' found in: {job_title[:50]}")
                break
        else:
            print(f"  ❌ No match in: {job_title[:50]}")

    match_ratio = matched / min(3, len(results))
    print(f"📊 Match ratio: {match_ratio:.0%} ({matched}/3 jobs)")
    return match_ratio >= min_keyword_match


#if the results are relevant, we can ask the LLM to rank them and explain why they are relevant

# async def ask(user_query):
#     results = hybrid_search(user_query, n_results=5)

#     # ── هل النتايج relevant؟ ──
#     if not results_are_relevant(user_query, results):
#         print(f"⚡ Results not relevant → Live scraping...")
        
#         from scraper.live_scraper import live_search_async, add_to_db
#         live_jobs = await live_search_async(user_query, num_pages=2)  # ← await
        
#         if live_jobs:
#             add_to_db(live_jobs)
#             results = [{"job": j, "score": 1.0} for j in live_jobs[:5]]
#             print(f"✅ Live scraping got {len(live_jobs)} jobs")
#         else:
#             print("❌ Live scraping found nothing")

#     if not results:
#         return "مش لاقي وظايف مناسبة، جرب كلمات تانية.", []

#     jobs_context = format_jobs_for_llm(results)

#     system_prompt = """أنت مساعد متخصص في إيجاد الوظائف في مصر.
#     - رد بالعربي الفصيح فقط
#     - كن مختصر ومفيد  
#     - رتّب الوظايف من الأنسب للأقل
#     - وضّح ليه كل وظيفة مناسبة في جملة واحدة
#     - دايماً حط الرابط في الآخر
#     - لو مفيش وظايف مناسبة قول بصراحة"""

#     user_prompt = f"""المستخدم بيدور على: "{user_query}"

#     الوظايف المتاحة:
#     {jobs_context}

#     رشّحله أنسب الوظايف مع شرح بسيط."""

#     response = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt}
#         ],
#         max_tokens=1000
#     )

#     return response.choices[0].message.content, results

async def ask_stream(user_query):
    """بترجع generator بيدي الكلام كلمة كلمة"""
    results = hybrid_search(user_query, n_results=15)

    if not results_are_relevant(user_query, results):
        from scraper.live_scraper import live_search_async, add_to_db
        live_jobs = await live_search_async(user_query)
        if live_jobs:
            add_to_db(live_jobs)
            results = [{"job": j, "score": 1.0} for j in live_jobs[:5]]

    jobs_context = format_jobs_for_llm(results)

    system_prompt = """أنت مساعد متخصص في إيجاد الوظائف في مصر.
    - رد بالعربي الفصيح فقط
    - كن مختصر ومفيد
    - رتّب الوظايف من الأنسب للأقل
    - وضّح ليه كل وظيفة مناسبة في جملة واحدة
    - لا تذكر أي روابط أو URLs — الروابط موجودة في الكاردز
    - اكتب فقط اسم الوظيفة والشركة وسبب المناسبة"""

    user_prompt = f"""المستخدم بيدور على: "{user_query}"
    الوظايف المتاحة:
    {jobs_context}
    رشّحله أنسب الوظايف مع شرح بسيط."""

    # ── Streaming ──
    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=1000,
        stream=True  # ← المهم
    )

    # ابعت الوظايف الأول كـ JSON
    jobs_data = []
    for r in results:
        job = r['job']
        jobs_data.append({
            "title":      job.get("title", "N/A"),
            "company":    job.get("company", "N/A"),
            "location":   job.get("location", "N/A"),
            "experience": job.get("experience", "N/A"),
            "level":      job.get("level", "N/A"),
            "job_type":   job.get("job_type", "N/A"),
            "url":        job.get("url", "#"),
            "source":     job.get("source", "wuzzuf"),  # ← أضف السطر ده
        })

    import json
    # أول message فيه الوظايف
    yield f"data: {json.dumps({'type': 'jobs', 'jobs': jobs_data})}\n\n"

    # بعدين ابعت الـ text كلمة كلمة
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield f"data: {json.dumps({'type': 'text', 'content': text})}\n\n"

    yield "data: [DONE]\n\n"


if __name__ == "__main__":
    ask_stream("عايز وظيفة python developer في القاهرة")
    print("\n" + "="*60 + "\n")
    ask_stream("أنا فريش جراد وعايز وظيفة customer service بالانجليزي")