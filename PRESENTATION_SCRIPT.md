# Presentation Script — ArXiv RAG Search Engine
### CSCE 670 | Texas A&M University | 9 Minutes Total
### Format: 5–6 min slides + 3–4 min live demo

---

## BEFORE YOU START
- **Check `.env`:** `LLM_PROVIDER=groq` and `GROQ_API_KEY=<your_key>` must be set — Ask mode silently fails without it
- Start server: `py -3.11 -m uvicorn backend.api:app` (start 5 min early — 25s cold start)
- Server running at `http://localhost:8000`
- Browser open on homepage, ready to go
- Gamma slides open in a separate tab
- Queries ready to paste:
  - `transformer attention mechanism`
  - `What are recent techniques for reducing hallucination in LLMs?`

---

## ── SLIDES SECTION (5:30) ──────────────────────────────

## [0:00 — 0:45] SLIDE 1: Motivation & System Overview

> "Hi everyone. The problem we set out to solve — when you're doing research, you don't just want a list of papers. You want answers. You want to know what the field says about your question, with sources you can verify.
>
> So we built a RAG-based academic search engine over 893,000 arXiv computer science papers. It has two modes — a Search mode that returns ranked paper results, and an Ask mode where you type a natural language question and get a cited, LLM-generated answer directly from the top papers. No hallucination — every claim is grounded in a real abstract."

---

## [0:45 — 1:30] SLIDE 2: Existing Systems & Limitations

> "Existing tools each solve part of the problem but not all of it.
>
> Google Scholar gives you keyword search — fast, but no semantic understanding and no answers. Semantic Scholar has better ranking but still just returns a list of papers. And tools like ChatGPT will generate answers, but they hallucinate paper titles and citations — you can't verify anything it says.
>
> Our system sits at the intersection — real retrieval over verified papers, combined with an LLM that only answers from what it actually retrieved. You get the answer AND the sources."

---

## [1:30 — 2:10] SLIDE 3: Data

> "Our dataset is the arXiv corpus from Cornell University, downloaded via Kaggle. The raw file is about 4 gigabytes — 2.97 million papers across all fields. We filtered down to computer science papers using the CS category tags, which gave us 892,992 papers.
>
> For each paper we use the title, abstract, authors, categories, and publication date. Because the file is so large, we process it line by line to avoid loading everything into memory at once. Papers are stored as JSONL — one JSON object per line — which lets the server stream through them efficiently at startup."

---

## [2:10 — 3:30] SLIDE 4: Implementation — Retrieval Pipeline

> "The core of the system is a four-stage retrieval pipeline.
>
> Stage one is BM25 — classic sparse keyword retrieval. It scores every paper based on how frequently the query terms appear, weighted by how rare those terms are across the whole corpus. Fast, no GPU needed, returns top 100 candidates.
>
> Stage two is dense retrieval. We use a model called all-MiniLM-L6-v2 — a lightweight sentence transformer from Microsoft — to encode the query into a 384-dimensional vector. We then search across 893,000 pre-computed paper embeddings using FAISS. This understands meaning, not just keywords — so a query about 'attention mechanism' can surface papers discussing 'self-attention' or 'query-key-value' even without exact word matches.
>
> Stage three is hybrid fusion using Reciprocal Rank Fusion — a technique from the IR literature. A paper that ranks highly in both BM25 and dense gets a boosted combined score.
>
> Stage four is cross-encoder re-ranking. We take the top 30 fused candidates and run them through ms-marco-MiniLM-L6-v2 — a cross-encoder that reads the query and each abstract together as a pair. This is much more accurate than comparing embeddings separately. It re-ranks those 30 and returns the best 10."

---

## [3:30 — 4:15] SLIDE 5: RAG & System Stack

> "For answer generation, we use Meta's Llama 3.3 70B model, served via the Groq API — we chose Groq specifically for its low latency, answers come back in about 2 to 3 seconds.
>
> The LLM is prompted to answer only from the retrieved abstracts and to cite papers by number — so every claim in the answer maps to a real paper the user can check.
>
> The backend is FastAPI with all models pre-loaded at startup, so there's no loading delay per request. We also built an in-memory caching layer — search results are cached up to 500 entries, ask answers up to 200. Repeated queries come back instantly without re-running retrieval or burning API credits.
>
> Search responses come back in under 2 seconds, Ask mode in about 5 seconds on the first query."

---

## [4:15 — 5:30] SLIDE 6: Evaluation Results

> "We evaluated the four retrieval methods using Precision at 5, nDCG at 10, and Mean Reciprocal Rank — standard IR metrics. Our test set has 10 queries with 10 relevant papers each, labeled using an LLM-as-judge approach via Groq.
>
> BM25 gets a P@5 of 0.60 — solid baseline. Dense retrieval actually underperforms BM25 at 0.38 — for precise CS terminology, keyword matching is still strong. Hybrid improves things slightly. And Hybrid with re-ranking hits perfect scores across all three metrics.
>
> The cross-encoder re-ranking is clearly the decisive component — nDCG@10 jumps from 0.51 to 1.0.
>
> One honest caveat — our relevance labels were generated from our own pipeline's output, so the Hybrid+Reranker scores reflect system consistency. We acknowledge this in the report and frame it as a demonstration of re-ranker effectiveness rather than absolute ground truth."

---

## ── LIVE DEMO SECTION (3:30) ────────────────────────────

## [5:30 — 6:10] DEMO: Search + Method Comparison
**SCREEN: Switch to browser, homepage visible**

> "Let me show it live. I'll search for 'transformer attention mechanism.'"

*Type query, hit Search. Wait for results.*

> "These are the top results using our full Hybrid+Reranker pipeline. Every result on this page is genuinely about attention mechanisms in Transformers — the re-ranker has pulled out exactly the right papers. Each card shows the title, authors, year, category tags, abstract excerpt, and relevance score. You can click the PDF link to go straight to arXiv.
>
> Now — the key demo feature."

*Click BM25 tab.*

> "Switching to BM25 only — pure keyword search. Notice the ranking changes."

*Click Dense tab.*

> "Dense only — semantic search with all-MiniLM-L6-v2. Different results again — it's finding papers about related concepts."

*Click Hybrid+Reranker tab.*

> "Back to the full pipeline — this is what gives us perfect precision in evaluation. Same query, four different rankings — you can see the IR concepts from this course in action."

---

## [6:10 — 7:20] DEMO: Ask Mode + Caching
**SCREEN: Click "ASK A QUESTION" toggle**

> "Now the Ask mode."

*Type: `What are recent techniques for reducing hallucination in LLMs?` — hit Search.*

> "This is a natural language research question. Under the hood, the system retrieves the top papers using the full pipeline, then sends those abstracts to Llama 3.3 70B on Groq with a prompt that says — answer only from these papers, cite them by number."

*Wait for answer to load (~3-5 seconds).*

> "And here's the result — a coherent cited answer with inline citations. [1], [2] — these map directly to the source papers shown below. Every claim is verifiable."

*Scroll down briefly to show paper cards.*

> "Now watch this —"

*Hit Search again with the same question.*

> "Instant. That's our caching layer — same query returns from cache without re-running retrieval or hitting the API again. Critical for a live demo and for keeping API costs down."

---

## [7:20 — 8:00] DEMO: Filters
**SCREEN: Back to Search mode with results visible**

*Search "graph neural networks" then use sidebar category filter.*

> "We also have sidebar filters — narrow by CS subcategory or year range. So if I filter to cs.LG — machine learning — results restrict to that field only. Useful when you want papers from a specific area."

---

## [8:00 — 8:30] WRAP UP
**SCREEN: Back to Gamma slide or results page**

> "To summarize — we built a complete RAG search engine over 893,000 arXiv papers. Four retrieval methods you can compare live. Cited LLM answers grounded in real abstracts. The re-ranker is the key component that takes retrieval from good to near-perfect.
>
> Everything is in our GitHub repo. Thank you."

---

## TIMING GUIDE

| Section | Duration | Cumulative |
|---------|----------|-----------|
| Motivation & Overview | 0:45 | 0:45 |
| Existing Systems | 0:45 | 1:30 |
| Data | 0:40 | 2:10 |
| Retrieval Pipeline | 1:20 | 3:30 |
| RAG & Stack | 0:45 | 4:15 |
| Evaluation Results | 1:15 | 5:30 |
| Demo: Search + Methods | 0:40 | 6:10 |
| Demo: Ask + Caching | 1:10 | 7:20 |
| Demo: Filters | 0:40 | 8:00 |
| Wrap up | 0:30 | 8:30 |
| **Buffer** | **0:30** | **9:00** |

---

## LIKELY Q&A

**Q: Why did dense retrieval underperform BM25?**
> "For precise CS terminology like 'graph neural networks node classification', exact keyword matching is very strong. Dense retrieval shines more on abstract or conceptual queries."

**Q: Why all-MiniLM-L6-v2 and not a larger model?**
> "It encodes 893K abstracts in about an hour on a consumer GPU. A larger model would take 3-4x longer and produce a bigger index. For this scale, MiniLM gives a good accuracy-speed tradeoff."

**Q: What's the caveat with your evaluation?**
> "Our relevance labels were generated by asking Groq to judge the top results from our own pipeline. So the Hybrid+Reranker scores reflect system consistency rather than fully independent ground truth. A stronger evaluation would use human annotators or an existing benchmark like BEIR."

**Q: Why Groq instead of OpenAI?**
> "Groq provides free-tier access with very low latency — answers in 2-3 seconds. It runs Meta's Llama 3.3 70B on custom LPU hardware, which is significantly faster than standard GPU inference."

**Q: Could this scale to all 2.97M arXiv papers?**
> "Yes — FAISS scales linearly. 3M papers would be roughly a 4.5GB index, still manageable. The main bottleneck would be encoding time — about 3-4 hours on GPU."
