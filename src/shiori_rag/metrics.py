"""Retrieval metrics at page level, for questions whose evidence is a list of page groups."""

import math
import random
from collections import defaultdict
from collections.abc import Callable

Page = tuple[str, int]  # (doc_id, pdf_page)
Retriever = Callable[[str, str], list[dict]]  # (question, lang) -> chunks, best first


def ranked_pages(chunks: list[dict]) -> list[Page]:
    """Chunks to pages: keep the best rank of each page, drop repeats."""
    seen, out = set(), []
    for chunk in chunks:
        page = (chunk["doc_id"], chunk["pdf_page"])
        if page not in seen:
            seen.add(page)
            out.append(page)
    return out


def evidence_groups(question: dict) -> list[set[Page]]:
    return [{(p["doc_id"], p["pdf_page"]) for p in g["pages"]} for g in question["evidence"]]


def score_question(question: dict, ranked: list[Page], k: int) -> dict:
    """Metrics for one answerable question, looking only at the top k pages."""
    groups, top = evidence_groups(question), ranked[:k]
    union = set().union(*groups)
    covered, dcg = set(), 0.0
    for rank, page in enumerate(top, start=1):
        for index, group in enumerate(groups):
            if index not in covered and page in group:
                covered.add(index)  # one page covers at most one group
                dcg += 1 / math.log2(rank + 1)
                break
    ideal = sum(1 / math.log2(rank + 1) for rank in range(1, min(len(groups), k) + 1))
    first = next((rank for rank, page in enumerate(top, start=1) if page in union), None)
    return {
        "hit": float(first is not None),
        "recall": len(covered) / len(groups),
        "complete": float(len(covered) == len(groups)),
        "rr": 1 / first if first else 0.0,
        "ndcg": dcg / ideal,
    }


def evaluate(questions: list[dict], retrieve: Retriever, k: int = 10) -> list[dict]:
    """One row of metrics per answerable question."""
    rows = []
    for q in questions:
        if not q["answerable"]:
            continue
        ranked = ranked_pages(retrieve(q["question"], q["lang"]))
        rows.append(
            {"id": q["id"], "lang": q["lang"], "type": q["type"], "split": q["split"],
             **score_question(q, ranked, k)}
        )
    return rows


def bootstrap_ci(values: list[float], n: int = 1000, seed: int = 0) -> tuple[float, float]:
    """95% interval for the mean, by resampling the questions with replacement."""
    rng = random.Random(seed)
    means = sorted(sum(rng.choices(values, k=len(values))) / len(values) for _ in range(n))
    return means[int(n * 0.025)], means[int(n * 0.975) - 1]


def summarize(rows: list[dict], by: str | None = None) -> dict[str, dict[str, float]]:
    """Mean of each metric, overall or grouped by a column such as lang or type."""
    buckets = defaultdict(list)
    for row in rows:
        buckets[row[by] if by else "all"].append(row)
    result = {}
    for name, items in buckets.items():
        result[name] = {"n": len(items)}
        for metric in ("hit", "recall", "complete", "rr", "ndcg"):
            values = [r[metric] for r in items]
            result[name][metric] = sum(values) / len(values)
        low, high = bootstrap_ci([r["hit"] for r in items])
        result[name]["hit_ci"] = (low, high)
    return result