"""Where do the questions already point, and what is still missing?"""

from collections import defaultdict

from shiori_rag.chunking import read_pages
from shiori_rag.evalset import load_questions

TARGETS = {
    "questions": 60,
    "japanese questions": 20,
    "unanswerable": 8,
    "cross-lingual": 6,
    "test split": 15,
    "multi-evidence (2+ groups)": 5,
}


def ranges(numbers: list[int]) -> str:
    out, start = [], None
    for index, n in enumerate(numbers):
        if start is None:
            start = n
        if index + 1 == len(numbers) or numbers[index + 1] != n + 1:
            out.append(str(start) if start == n else f"{start}-{n}")
            start = None
    return ", ".join(out) or "none"


pages, questions = read_pages(), load_questions()
used = defaultdict(set)
for q in questions:
    for group in q["evidence"]:
        for page in group["pages"]:
            used[page["doc_id"]].add(page["pdf_page"])

print("Pages used as evidence (pages that are not near-empty):")
for doc_id in dict.fromkeys(p["doc_id"] for p in pages):
    content = [p["pdf_page"] for p in pages if p["doc_id"] == doc_id and "near_empty" not in p["flags"]]
    missing = [n for n in content if n not in used[doc_id]]
    name = doc_id.replace("meti_trade_wp_", "")
    print(f"  {name[:50]:<52}{len(content) - len(missing):>3}/{len(content):<3} never used: {ranges(missing)}")

counts = {
    "questions": len(questions),
    "japanese questions": sum(q["lang"] == "ja" for q in questions),
    "unanswerable": sum(not q["answerable"] for q in questions),
    "cross-lingual": sum(q["type"] == "cross-lingual" for q in questions),
    "test split": sum(q["split"] == "test" for q in questions),
    "multi-evidence (2+ groups)": sum(len(q["evidence"]) >= 2 for q in questions),
}
print(f"\n{'target':<30}{'have':>5}{'goal':>6}  need")
for name, goal in TARGETS.items():
    print(f"{name:<30}{counts[name]:>5}{goal:>6}  {max(goal - counts[name], 0)}")
print(f"\nnot verified yet: {sum(not q['verified'] for q in questions)}")