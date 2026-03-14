# API/main.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pathlib  # Import the whole module to avoid naming conflicts
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from RAG.pipeline import ask_stream, hybrid_search
# CV mathcer
from fastapi import UploadFile, File
from RAG.cv_matcher import match_cv_to_jobs
from groq import Groq
from dotenv import load_dotenv
import json


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# Groq for cv reading
groq_client = Groq(api_key=GROQ_API_KEY)

# init faskapi server
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static Files ──
app.mount("/src", StaticFiles(directory="src"), name="src")


class SearchRequest(BaseModel):
    query: str

# streaming

@app.post("/search/stream")
async def search_stream(req: SearchRequest):
    return StreamingResponse(
        ask_stream(req.query),
        media_type="text/event-stream"
    )

# CV matching

@app.post("/cv-match")
async def cv_match(file: UploadFile = File(...)):
    # اقرأ الـ PDF
    pdf_bytes = await file.read()

    # جيب الـ matches
    matches, skills_profile = match_cv_to_jobs(pdf_bytes, n_results=5)

    if not matches:
        return {"error": "مش قادر أقرأ الـ CV"}

    # اسأل الـ LLM يشرح النتايج
    jobs_text = "\n".join([
        f"- {m['title']} @ {m['company']} ({m['match']}% match)"
        for m in matches
    ])

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""بناءً على الـ CV، دي أنسب الوظايف:
            {jobs_text}

            اشرح بالعربي ليه الوظايف دي مناسبة في 3 جمل بس."""
        }],
        max_tokens=300
    )

    return {
        "matches": matches,
        "summary": response.choices[0].message.content
    }



# non-streaming (for testing/debugging)

@app.post("/search")
async def search(req: SearchRequest):
    # results = hybrid_search(req.query, n_results=5)
    # answer = ask(req.query)

    answer, results = await ask_stream(req.query)  # ask() بترجع answer (اللي هيرجع للـ LLM) و results (الوظايف اللي هتترجع للـ frontend)

    
    jobs = []
    for r in results:
        job = r['job']
        jobs.append({
            "title":      job.get("title", "N/A"),
            "company":    job.get("company", "N/A"),
            "location":   job.get("location", "N/A"),
            "experience": job.get("experience", "N/A"),
            "level":      job.get("level", "N/A"),
            "job_type":   job.get("job_type", "N/A"),
            "url":        job.get("url", "#"),
            "score":      r['score']
        })
    
        # debug - شوف إيه اللي بيترجع
    print(f"Jobs found: {len(jobs)}")
    print(f"First job: {jobs[0] if jobs else 'NONE'}")
    
    return {"answer": answer, "jobs": jobs}

@app.get("/")
async def root():
    return FileResponse("index.html")