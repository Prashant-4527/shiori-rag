"""BM25 ranking written from scratch, plus a retriever that plugs into the evaluation code."""

import math
from collections import Counter, defaultdict

from shiori_rag.tokenization import tokenize


class BM25:
    """Okapi BM25 with the non-negative IDF used by Lucene.

    score(doc, query) = sum over query terms t of
        idf(t) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(doc) / avg_len))
    """

    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.lengths = [len(d) for d in docs]
        self.avg_len = sum(self.lengths) / len(docs)
        doc_freq = Counter(term for d in docs for term in set(d))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in doc_freq.items()}
        self.postings = defaultdict(list)  # term -> [(doc index, term frequency)]
        for index, doc in enumerate(docs):
            for term, freq in Counter(doc).items():
                self.postings[term].append((index, freq))

    def scores(self, query: list[str]) -> dict[int, float]:
        """Score every document that shares at least one term with the query."""
        result = defaultdict(float)
        for term in query:
            idf = self.idf.get(term)
            if idf is None:
                continue
            for index, freq in self.postings[term]:
                norm = 1 - self.b + self.b * self.lengths[index] / self.avg_len
                result[index] += idf * freq * (self.k1 + 1) / (freq + self.k1 * norm)
        return result


class Bm25Retriever:
    """Callable (question, lang) -> chunks, best first."""

    def __init__(self, chunks: list[dict], mode: str = "C", top_k: int = 10, **params):
        self.chunks, self.mode, self.top_k = chunks, mode, top_k
        self.index = BM25([tokenize(c["text_search"], c["lang"], mode) for c in chunks], **params)

    def __call__(self, question: str, lang: str) -> list[dict]:
        scores = self.index.scores(tokenize(question, lang, self.mode))
        best = sorted(scores, key=lambda i: (-scores[i], i))[: self.top_k]
        return [self.chunks[i] for i in best]