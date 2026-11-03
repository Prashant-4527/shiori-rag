"""Add one verified question to eval/questions.jsonl, finding its evidence pages interactively."""

import json

from shiori_rag.chunking import read_pages
from shiori_rag.evalset import QUESTIONS, TYPES, load_questions, validate
from shiori_rag.normalize import search_form

pages = read_pages()


def ask(prompt: str, default: str = "") -> str:
    shown = f" [{default}]" if default else ""
    return input(f"{prompt}{shown}: ").strip() or default


def search(phrase: str) -> list[tuple[dict, str]]:
    needle = search_form(phrase).lower()
    hits = []
    for page in pages:
        text = page["text_search"].lower()
        at = text.find(needle)
        if at != -1:
            hits.append((page, text[max(0, at - 40) : at + len(needle) + 40].replace("\n", " ")))
    return hits


def pick_group() -> dict | None:
    while True:
        phrase = ask("Search phrase for an evidence group (blank = no more groups)")
        if not phrase:
            return None
        hits = search(phrase)
        if not hits:
            print("  no page contains that phrase")
            continue
        for number, (page, snippet) in enumerate(hits, start=1):
            name = page["doc_id"].replace("meti_trade_wp_", "")
            print(f"  {number:>2}. {name} p{page['pdf_page']}: ...{snippet}...")
        chosen = ask("Numbers of the pages that really support the answer (comma separated)")
        picks = [
            hits[int(n) - 1][0]
            for n in chosen.split(",")
            if n.strip().isdigit() and 0 < int(n) <= len(hits)
        ]
        if picks:
            return {"pages": [{"doc_id": p["doc_id"], "pdf_page": p["pdf_page"]} for p in picks]}


def main() -> None:
    questions = load_questions()
    number = max(int(q["id"][1:]) for q in questions) + 1
    lang = ask("Language (en/ja)", "ja")
    kind = ask(f"Type {sorted(TYPES)}", "factual")
    question = ask("Question")
    answer = ask("Reference answer")
    split = ask("Split (dev/test)", "dev")
    evidence = []
    if kind != "unanswerable":
        while (group := pick_group()) is not None:
            evidence.append(group)
    new = {
        "id": f"q{number:03d}", "lang": lang, "type": kind, "corpus": "trade",
        "question": question, "answer": answer, "answerable": kind != "unanswerable",
        "evidence": evidence, "origin": "hand", "verified": True, "split": split, "notes": "",
    }
    problems = validate([*questions, new], pages)
    if problems:
        print("Not saved:", *problems, sep="\n  ")
        return
    with QUESTIONS.open("ab") as fh:
        if QUESTIONS.stat().st_size and not QUESTIONS.read_bytes().endswith(b"\n"):
            fh.write(b"\n")
        fh.write((json.dumps(new, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"Saved {new['id']}")


if __name__ == "__main__":
    main()