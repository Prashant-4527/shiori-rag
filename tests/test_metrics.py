import math
import random

from shiori_rag.metrics import bootstrap_ci, evaluate, ranked_pages, score_question, summarize

A, B, C, D = ("d", 1), ("d", 2), ("d", 3), ("d", 4)


def question(*groups, answerable=True, qid="q", lang="en", kind="factual"):
    return {
        "id": qid, "lang": lang, "type": kind, "split": "dev", "question": "?",
        "answerable": answerable,
        "evidence": [{"pages": [{"doc_id": d, "pdf_page": p} for d, p in g]} for g in groups],
    }


def test_ranked_pages_keeps_best_rank_and_drops_repeats():
    chunks = [{"doc_id": "d", "pdf_page": 1}, {"doc_id": "d", "pdf_page": 1}, {"doc_id": "d", "pdf_page": 2}]
    assert ranked_pages(chunks) == [A, B]


def test_correct_page_at_rank_three():
    s = score_question(question([C]), [A, B, C], k=5)
    assert s["hit"] == 1 and s["rr"] == 1 / 3
    assert math.isclose(s["ndcg"], 1 / math.log2(4))


def test_cutoff_hides_pages_beyond_k():
    s = score_question(question([C]), [A, B, C], k=2)
    assert s == {"hit": 0.0, "recall": 0.0, "complete": 0.0, "rr": 0.0, "ndcg": 0.0}


def test_any_page_in_a_group_counts_and_repeats_add_nothing():
    s = score_question(question([A, B]), [A, B, C], k=5)
    assert s["ndcg"] == 1.0 and s["rr"] == 1.0


def test_two_groups_need_a_page_from_each():
    q = question([A], [C])
    s = score_question(q, [A, B, C], k=5)
    assert s["recall"] == 1.0 and s["complete"] == 1.0
    assert math.isclose(s["ndcg"], (1 + 1 / math.log2(4)) / (1 + 1 / math.log2(3)))
    half = score_question(q, [A, B, D], k=5)
    assert half["recall"] == 0.5 and half["complete"] == 0.0


def test_evaluate_skips_unanswerable_and_calls_the_retriever_with_language():
    seen = []

    def retrieve(text, lang):
        seen.append(lang)
        return [{"doc_id": "d", "pdf_page": 1}]

    qs = [question([A], lang="ja", qid="q1"), question(answerable=False, qid="q2", kind="unanswerable")]
    rows = evaluate(qs, retrieve, k=5)
    assert [r["id"] for r in rows] == ["q1"] and seen == ["ja"]


def test_sanity_perfect_retriever_scores_one_and_random_scores_low():
    qs = [question([("d", n)], qid=f"q{n}") for n in range(1, 41)]
    for q in qs:
        q["question"] = q["id"]
    gold = {q["id"]: q["evidence"][0]["pages"][0]["pdf_page"] for q in qs}

    def perfect(text, lang):
        return [{"doc_id": "d", "pdf_page": gold[text]}]

    rng = random.Random(1)

    def shuffled(text, lang):
        return [{"doc_id": "d", "pdf_page": n} for n in rng.sample(range(1, 41), 40)]

    assert summarize(evaluate(qs, perfect, k=5))["all"]["hit"] == 1.0
    assert summarize(evaluate(qs, shuffled, k=5))["all"]["hit"] < 0.4


def test_bootstrap_interval_contains_the_mean_and_shrinks_with_more_data():
    small = [1.0, 0.0] * 5
    large = [1.0, 0.0] * 50
    lo, hi = bootstrap_ci(small)
    assert lo <= 0.5 <= hi
    lo2, hi2 = bootstrap_ci(large)
    assert (hi2 - lo2) < (hi - lo)