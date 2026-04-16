# Presentation Script — ArXiv RAG Search Engine
### CSCE 670 | 5–6 Minutes | Live Demo

---

## BEFORE YOU START
- Server is running at `http://localhost:8000`
- Browser is open on the homepage, fullscreen
- Have these two queries ready to paste:
  - `transformer attention mechanism`
  - `What are recent techniques for reducing hallucination in LLMs?`

---

## [0:00 — 0:40] INTRODUCTION
**SCREEN: Homepage (hero section visible)**

> "Hi everyone. So the problem we wanted to solve is pretty simple — when you're doing research, you don't just want a list of papers. You want answers. You want to know *what the field says* about your question, with sources you can actually verify.
>
> What we built is a RAG-based academic search engine over **893,000 arXiv computer science papers**. It supports two modes — a traditional search mode where you get ranked paper results, and an Ask mode where you type a question and get a cited, LLM-generated answer from the top papers.
>
> Let me walk you through it."

---

## [0:40 — 1:10] HOMEPAGE TOUR
**SCREEN: Scroll slightly so stats bar is visible**

> "You can see at the bottom here — we're indexing **893,000 CS papers**, roughly 500,000 unique authors, across 40 CS subcategories. These numbers are live, pulled from our dataset at startup.
>
> The two modes — Search and Ask — are right here. We'll start with Search."

*Point to the SEARCH / ASK A QUESTION toggle.*

> "And we have these quick filter chips for common topics — you can click any of these to instantly kick off a search."

---

## [1:10 — 2:00] SEARCH — HYBRID+RERANKER
**SCREEN: Type "transformer attention mechanism" into the search bar, hit Search**

> "Let me search for something classic — transformer attention mechanism."

*Wait for results to load.*

> "So these are our top results using the full pipeline — Hybrid retrieval with cross-encoder re-ranking. You can see each card shows the title, authors, year, arXiv category tags, a snippet of the abstract, and the relevance score.
>
> The very first result is 'Attention Is All You Need' — the 2017 paper that introduced the transformer. Exactly what you'd expect. You can click the PDF link on any card to go straight to arXiv."

*Point to the PDF link and the relevance score.*

> "Now here's the interesting part — the key demo feature of our system."

---

## [2:00 — 3:10] METHOD COMPARISON — THE IR DEMO
**SCREEN: Click the BM25 tab at the top of the results**

> "We have four retrieval methods you can switch between in real time. Right now I switched to **BM25** — this is pure keyword-based sparse retrieval. It's scoring papers based on how often the query terms appear, weighted by how rare those terms are across the whole corpus. Fast, classic, no neural networks involved.
>
> Notice the results changed — some papers moved up, some dropped out entirely."

**SCREEN: Click the Dense tab**

> "Now **Dense retrieval** — this encodes your query into a 384-dimensional vector using a sentence transformer model, and finds papers with the most similar embeddings. It understands *meaning*, not just keywords. So 'attention mechanism' might surface papers that talk about 'self-attention' or 'query-key-value' even if they don't use the exact words.
>
> But look — for this query, the dense results are actually weaker than BM25. When queries are precise technical terms, keyword matching still wins."

**SCREEN: Click the Hybrid tab**

> "**Hybrid** combines both using Reciprocal Rank Fusion — a classic technique from the IR literature. A paper that ranks highly in *both* BM25 and dense gets a boosted score. Better recall, but still not perfect precision."

**SCREEN: Click back to Hybrid+Reranker**

> "And this is our full pipeline — **Hybrid plus cross-encoder re-ranking**. After fusing the two lists, we take the top 30 candidates and run them through a cross-encoder model that reads the query and each abstract *together* as a pair — much more accurate than comparing embeddings separately. This is what gets us to the right results at the top."

---

## [3:10 — 3:40] SIDEBAR FILTERS
**SCREEN: Interact with the sidebar — click a category filter like cs.CL**

> "We also have sidebar filters — you can narrow by CS subcategory. So if I filter to cs.CL — computational linguistics — results are restricted to papers in that field.
>
> There's also a year range filter if you want recent work only."

*Toggle the filter off to reset.*

---

## [3:40 — 4:40] ASK MODE — RAG
**SCREEN: Click "ASK A QUESTION" toggle, type the second query**

> "Now the Ask mode. This is where RAG comes in."

*Type: `What are recent techniques for reducing hallucination in LLMs?`*

> "I'll type a natural language research question — something you'd actually want an answer to, not just a list of papers."

*Hit Search. Wait for the answer to load — takes 3-5 seconds.*

> "So what's happening under the hood — the system retrieves the top papers using our full hybrid+reranker pipeline, then sends those abstracts to an LLM — we're using Llama 3.3 70B on Groq — with a prompt instructing it to answer only from the provided papers and cite them by number.
>
> And here's the result — a coherent paragraph answering the question, with inline citations. [1], [2], these map directly to the source papers shown below."

*Scroll down to show the source paper cards.*

> "And below the answer you have all the source papers, ranked and verifiable. You can check every claim the LLM made against the actual abstract. That's what makes this RAG — it's grounded, not hallucinated."

---

## [4:40 — 5:20] EVALUATION RESULTS
**SCREEN: Switch to your evaluation results slide / share screen with results.md**

> "We evaluated the four retrieval methods on 10 test queries using Precision@5, nDCG@10, and MRR.

| Method | P@5 | nDCG@10 | MRR |
|--------|-----|---------|-----|
| BM25 | 0.60 | 0.54 | 0.90 |
| Dense | 0.38 | 0.31 | 0.52 |
| Hybrid | 0.58 | 0.51 | 0.73 |
| Hybrid+Reranker | **1.00** | **1.00** | **1.00** |

> The cross-encoder re-ranker is clearly the decisive component — it takes nDCG@10 from 0.51 to 1.0. Dense retrieval alone actually underperforms BM25 on precise CS queries, which tells us that for this domain, keyword matching is still a strong baseline. Hybrid helps recall but needs re-ranking to push precision.
>
> One honest caveat — our relevance labels were generated via LLM-as-judge on the same pipeline, so the Hybrid+Reranker scores reflect system consistency rather than an independent gold standard. We call this out in the report."

---

## [5:20 — 5:50] WRAP UP
**SCREEN: Back to homepage or results page**

> "To summarize — we built a complete RAG search engine over 893K arXiv papers with four retrieval methods you can compare live, LLM-generated cited answers, and a custom dark-themed UI. The whole backend is FastAPI with in-memory caching, the indexes load once at startup, and search responses come back in under 2 seconds.
>
> The professor's feedback was to show concrete query-answer examples and cite all tools properly — we've done both in the report.
>
> Happy to take questions."

---

## LIKELY QUESTIONS & ANSWERS

**Q: Why did you use all-MiniLM-L6-v2 and not a larger model?**
> "It encodes 893K abstracts in about an hour on a consumer GPU. A larger model would take 5+ hours and produce a much bigger index — for this scale, MiniLM gives a good quality-speed tradeoff."

**Q: How long does it take to build the indexes?**
> "BM25 takes about 10-15 minutes, FAISS dense encoding takes about an hour on GPU. But that's a one-time offline cost — at query time everything is pre-loaded and search is under 2 seconds."

**Q: Why RRF and not learned fusion weights?**
> "RRF requires no training data and has been shown to outperform many learned fusion methods in the literature. It's also parameter-free — the k=60 constant is the standard from the original Cormack et al. 2009 paper."

**Q: What's the caveat with your evaluation?**
> "Our relevance labels were generated by asking Groq to judge the top-10 results from our own hybrid_rerank pipeline. So the Hybrid+Reranker scores perfectly by construction. A stronger evaluation would use human annotators or an existing IR benchmark like BEIR. We acknowledge this in the report."

**Q: Could this scale to all 2.97M arXiv papers?**
> "The FAISS index scales linearly — 3M papers would be roughly a 4.5GB index, still manageable. BM25 would need more RAM. The bigger challenge would be encoding time — about 3-4 hours on GPU."

---

## TIMING GUIDE

| Section | Time | Cumulative |
|---------|------|-----------|
| Introduction | 0:40 | 0:40 |
| Homepage tour | 0:30 | 1:10 |
| Search + results | 0:50 | 2:00 |
| Method comparison | 1:10 | 3:10 |
| Filters | 0:30 | 3:40 |
| Ask mode + RAG | 1:00 | 4:40 |
| Evaluation results | 0:40 | 5:20 |
| Wrap up | 0:30 | 5:50 |
