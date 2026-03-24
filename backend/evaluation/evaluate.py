"""
Evaluation script — computes P@5, nDCG@10, MRR across retrieval configurations.
Run after indexes are built and the API server is running.
"""
import json
import math
import requests
from pathlib import Path

EVAL_PATH = Path(__file__).parent / "test_queries.json"
API_BASE = "http://localhost:8000"
METHODS = ["bm25", "dense", "hybrid", "hybrid_rerank"]


def precision_at_k(relevant: set, retrieved: list, k: int) -> float:
    top_k = retrieved[:k]
    hits = sum(1 for doc_id in top_k if doc_id in relevant)
    return hits / k


def dcg_at_k(relevant: set, retrieved: list, k: int) -> float:
    dcg = 0.0
    for i, doc_id in enumerate(retrieved[:k], start=1):
        if doc_id in relevant:
            dcg += 1.0 / math.log2(i + 1)
    return dcg


def ndcg_at_k(relevant: set, retrieved: list, k: int) -> float:
    ideal = sorted([1] * min(len(relevant), k) + [0] * max(k - len(relevant), 0), reverse=True)
    ideal_dcg = sum(g / math.log2(i + 2) for i, g in enumerate(ideal[:k]))
    if ideal_dcg == 0:
        return 0.0
    return dcg_at_k(relevant, retrieved, k) / ideal_dcg


def mean_reciprocal_rank(relevant: set, retrieved: list) -> float:
    for i, doc_id in enumerate(retrieved, start=1):
        if doc_id in relevant:
            return 1.0 / i
    return 0.0


def run_search(query: str, method: str, top_k: int = 10) -> list[str]:
    resp = requests.get(
        f"{API_BASE}/api/search",
        params={"q": query, "method": method, "top_k": top_k},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return [r["id"] for r in data["results"]]


def evaluate():
    if not EVAL_PATH.exists():
        raise FileNotFoundError(f"Test queries not found at {EVAL_PATH}")

    with open(EVAL_PATH) as f:
        test_queries = json.load(f)

    print(f"Evaluating {len(test_queries)} queries across {len(METHODS)} methods...\n")

    aggregate: dict[str, dict] = {m: {"p5": [], "ndcg10": [], "mrr": []} for m in METHODS}

    for item in test_queries:
        query = item["query"]
        relevant_ids = set(item["relevant_ids"])
        print(f"Query: {query!r}")

        for method in METHODS:
            retrieved = run_search(query, method, top_k=10)
            p5     = precision_at_k(relevant_ids, retrieved, 5)
            ndcg10 = ndcg_at_k(relevant_ids, retrieved, 10)
            mrr    = mean_reciprocal_rank(relevant_ids, retrieved)
            aggregate[method]["p5"].append(p5)
            aggregate[method]["ndcg10"].append(ndcg10)
            aggregate[method]["mrr"].append(mrr)
            print(f"  {method:20s}  P@5={p5:.3f}  nDCG@10={ndcg10:.3f}  MRR={mrr:.3f}")
        print()

    print("=" * 60)
    print(f"{'Method':<22} {'P@5':>8} {'nDCG@10':>10} {'MRR':>8}")
    print("-" * 60)
    for method in METHODS:
        scores = aggregate[method]
        n = len(scores["p5"])
        mp5     = sum(scores["p5"])     / n
        mndcg10 = sum(scores["ndcg10"]) / n
        mmrr    = sum(scores["mrr"])    / n
        print(f"{method:<22} {mp5:>8.4f} {mndcg10:>10.4f} {mmrr:>8.4f}")
    print("=" * 60)


if __name__ == "__main__":
    evaluate()
