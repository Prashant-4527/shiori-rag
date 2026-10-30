"""Audit the questions for copied wording (lexical leakage) and balance."""

import re
from collections import Counter, defaultdict

from shiori_rag.chunking import japanese_words, read_pages
from shiori_rag.evalset import load_questions
from shiori_rag.normalize import search_form

N = 3  # shingle size in tokens
FLAG = 0.5  # share of the question's shingles found on the evidence pages


def tokens(text: str, lang: str) -> list[str]:
    text = search_form(text).lower()
    if lang == "ja":
        return [
            w for w in japanese_words(text) if w.strip() and not re.fullmatch(r"\W+", w)
        ]
    return re.findall(r"\w+", text)


def shingles(items: list[str]) -> set[tuple[str, ...]]:
    return {tuple(items[i : i + N]) for i in range(len(items) - N + 1)}


pages = {(p["doc_id"], p["pdf_page"]): p for p in read_pages()}
questions = load_questions()
overlap_by_lang = defaultdict(list)

print(f"{'id':<6}{'lang':<5}{'type':<15}{'overlap':>8}  note")
for q in questions:
    if not q["answerable"]:
        continue
    same_language = [
        pages[(p["doc_id"], p["pdf_page"])]
        for group in q["evidence"]
        for p in group["pages"]
        if pages[(p["doc_id"], p["pdf_page"])]["lang"] == q["lang"]
    ]
    if not same_language:
        print(
            f"{q['id']:<6}{q['lang']:<5}{q['type']:<15}{'-':>8}  evidence only in the other language"
        )
        continue
    asked = shingles(tokens(q["question"], q["lang"]))
    evidence = set().union(
        *(shingles(tokens(p["text"], q["lang"])) for p in same_language)
    )
    score = len(asked & evidence) / max(len(asked), 1)
    overlap_by_lang[q["lang"]].append(score)
    print(
        f"{q['id']:<6}{q['lang']:<5}{q['type']:<15}{score:>8.2f}  {'COPIED WORDING?' if score >= FLAG else ''}"
    )

print()
for lang, scores in overlap_by_lang.items():
    print(
        f"{lang}: mean overlap {sum(scores) / len(scores):.2f} over {len(scores)} questions"
    )
print("by language:", dict(Counter(q["lang"] for q in questions)))
print("by type:    ", dict(Counter(q["type"] for q in questions)))
print("by split:   ", dict(Counter(q["split"] for q in questions)))
