<div align="center">



## 🚀 تشغيل المشروع


### الخطوة 1 — استنساخ المشروع

```bash
git clone https://github.com/Hazem-nabil42/Jobs-Internships-Hybrid-RAG-finder.git
cd Jobs-Internships-Hybrid-RAG-finder
```

### الخطوة 2 — الإعداد الأولي (مرة واحدة فقط ✅)

```bash
python setup.py
```

> 📌 هذا الأمر يثبّت جميع المكتبات المطلوبة ويهيئ البيئة تلقائيًا.

### الخطوة 3 — بناء Tailwind CSS

```bash
npx tailwindcss -i ./src/css/input.css -o ./src/css/output.css
```

### الخطوة 4 — تشغيل الخادم

```bash
uvicorn API.main:app --reload
```

### الخطوة 5 — افتح المتصفح 🌐

```
http://localhost:8000
```

---

## 🔬 كيف يعمل النظام؟

```mermaid
flowchart LR
    A[🔎 User Query] --> B{Hybrid Retriever}
    B --> C[Vector Datavase search\nSemantic Embeddings]
    B --> D[\nBM25 Keywords search]
    C --> E[top 10 relevent \n vector embeddings]
    D --> E
    E --> F[📊 Re-ranker]
    F --> G[✅ Top Results]
    G --> H[💬 LLM Response]
```

---


<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2c5364,50:203a43,100:0f2027&height=120&section=footer" />

**صُنع بـ ❤️ لدعم الباحثين عن عمل في مصر**

⭐ إذا أعجبك المشروع، لا تنسَ تضع نجمة!

[![GitHub stars](https://img.shields.io/github/stars/Hazem-nabil42/Jobs-Internships-Hybrid-RAG-finder?style=social)](https://github.com/Hazem-nabil42/Jobs-Internships-Hybrid-RAG-finder)

</div>
