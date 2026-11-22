import math

from shiori_rag.bm25 import BM25, Bm25Retriever
from shiori_rag.tokenization import tokenize


def test_score_matches_the_formula_by_hand():
    docs = [["a", "b"], ["a", "c"], ["d"]]
    idf = math.log(1 + (3 - 2 + 0.5) / (2 + 0.5))  # "a" is in 2 of 3 documents
    norm = 1 - 0.75 + 0.75 * 2 / (5 / 3)  # document length 2, average length 5/3
    expected = idf * 1 * 2.5 / (1 + 1.5 * norm)
    assert math.isclose(BM25(docs).scores(["a"])[0], expected)


def test_unknown_terms_score_nothing():
    assert BM25([["a"], ["b"]]).scores(["zzz"]) == {}


def test_shorter_document_wins_with_equal_term_frequency():
    scores = BM25([["a", "x", "y", "z", "w"], ["a"]]).scores(["a"])
    assert scores[1] > scores[0]


def test_rare_term_outweighs_common_term():
    docs = [["the", "tariff"], ["the", "growth"], ["the", "trade"], ["the", "china"]]
    scores = BM25(docs).scores(["the", "tariff"])
    assert max(scores, key=scores.get) == 0


def test_more_occurrences_score_higher_but_with_diminishing_returns():
    docs = [["a"] + ["x"] * 7, ["a"] * 2 + ["x"] * 6, ["a"] * 4 + ["x"] * 4, ["a"] * 8]
    s = BM25(docs).scores(["a"])
    assert s[0] < s[1] < s[2] < s[3]
    assert (s[1] - s[0]) / 1 > (s[2] - s[1]) / 2 > (s[3] - s[2]) / 4


def test_japanese_modes_split_compounds_differently():
    short = tokenize("経済産業省は発表した。", "ja", "A")
    long = tokenize("経済産業省は発表した。", "ja", "C")
    assert "経済産業省" in long and "経済産業省" not in short
    assert all(t.strip() and t not in {"。", "、"} for t in long)


def test_english_tokenizer_lowercases_and_drops_punctuation():
    assert tokenize("Growth was 3.3%, solid.", "en") == ["growth", "was", "3", "3", "solid"]


def test_retriever_returns_best_chunks_first_and_is_deterministic():
    chunks = [
        {"text_search": "tariff shock raised uncertainty", "lang": "en", "doc_id": "d", "pdf_page": 1},
        {"text_search": "supply chain resilience", "lang": "en", "doc_id": "d", "pdf_page": 2},
        {"text_search": "tariff rates by country table", "lang": "en", "doc_id": "d", "pdf_page": 3},
    ]
    retrieve = Bm25Retriever(chunks, top_k=2)
    first = retrieve("tariff uncertainty", "en")
    assert [c["pdf_page"] for c in first] == [1, 3]
    assert retrieve("tariff uncertainty", "en") == first
    assert retrieve("zzz", "en") == []