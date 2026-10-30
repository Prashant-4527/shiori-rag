"""Load and validate the evaluation questions."""

import json
from pathlib import Path

from shiori_rag.config import PROJECT_ROOT

QUESTIONS = PROJECT_ROOT / "eval" / "questions.jsonl"
REQUIRED = [
    "id",
    "lang",
    "type",
    "question",
    "answer",
    "answerable",
    "evidence",
    "origin",
    "verified",
    "split",
]
LANGS = {"en", "ja"}
SPLITS = {"dev", "test"}
TYPES = {
    "numeric",
    "factual",
    "list",
    "summary",
    "comparison",
    "cross-lingual",
    "unanswerable",
}


def load_questions(path: Path = QUESTIONS) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def validate(
    questions: list[dict], pages: list[dict], strict: bool = False
) -> list[str]:
    """Return a list of problems. An empty list means the set is consistent."""
    known = {(p["doc_id"], p["pdf_page"]) for p in pages}
    problems, seen = [], set()
    for q in questions:
        qid = q.get("id", "?")
        for key in REQUIRED:
            if key not in q:
                problems.append(f"{qid}: missing field '{key}'")
        if qid in seen:
            problems.append(f"{qid}: duplicate id")
        seen.add(qid)
        if q.get("lang") not in LANGS:
            problems.append(f"{qid}: lang must be one of {sorted(LANGS)}")
        if q.get("split") not in SPLITS:
            problems.append(f"{qid}: split must be one of {sorted(SPLITS)}")
        if q.get("type") not in TYPES:
            problems.append(f"{qid}: unknown type '{q.get('type')}'")
        if not str(q.get("question", "")).strip():
            problems.append(f"{qid}: empty question")
        groups = q.get("evidence", [])
        if q.get("answerable"):
            if not groups or any(not g["pages"] for g in groups):
                problems.append(f"{qid}: answerable but has an empty evidence group")
            if q.get("type") == "unanswerable":
                problems.append(f"{qid}: type is unanswerable but answerable is true")
        else:
            if groups:
                problems.append(f"{qid}: unanswerable questions must have no evidence")
            if q.get("type") != "unanswerable":
                problems.append(
                    f"{qid}: answerable is false but type is '{q.get('type')}'"
                )
        for group in groups:
            for page in group["pages"]:
                if (page["doc_id"], page["pdf_page"]) not in known:
                    problems.append(
                        f"{qid}: unknown page {page['doc_id']} p{page['pdf_page']}"
                    )
        if strict and not q.get("verified"):
            problems.append(f"{qid}: not verified yet")
    return problems
