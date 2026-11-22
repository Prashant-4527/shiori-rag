"""BM25 baseline: chunk size and Sudachi split mode, scored on the dev questions only."""

import argparse

from shiori_rag.bm25 import Bm25Retriever
from shiori_rag.chunking import chunk_corpus, read_pages
from shiori_rag.evalset import load_questions
from shiori_rag.metrics import evaluate, ranked_pages, summarize

parser = argparse.ArgumentParser()
parser.add_argument("--failures", action="store_true", help="print the questions that miss the top 5")
parser.add_argument("--size", type=int, default=400)
parser.add_argument("--overlap", type=int, default=60)
parser.add_argument("--mode", default="C", choices=["A", "B", "C"])
args = parser.parse_args()

pages = read_pages()
dev = [q for q in load_questions() if q["split"] == "dev"]  # the test split stays sealed


def short(page):
    return f"{page[0].replace('meti_trade_wp_', '')[:34]} p{page[1]}"


if args.failures:
    chunks = chunk_corpus(pages, args.size, args.overlap)
    retrieve = Bm25Retriever(chunks, args.mode)
    rows = {r["id"]: r for r in evaluate(dev, retrieve, k=5)}
    for q in dev:
        if q["answerable"] and rows[q["id"]]["hit"] == 0:
            gold = {(p["doc_id"], p["pdf_page"]) for g in q["evidence"] for p in g["pages"]}
            print(f"\n{q['id']} [{q['lang']}, {q['type']}] {q['question']}")
            print("  gold:", "; ".join(short(p) for p in sorted(gold)[:4]))
            for page in ranked_pages(retrieve(q["question"], q["lang"]))[:3]:
                print("  got :", short(page))
    raise SystemExit

print(f"{len(dev)} dev questions, {sum(q['answerable'] for q in dev)} answerable\n")
print(
    f"{'chunks':<12}{'mode':<5}{'hit@5':>7}{'(95% CI)':>14}{'hit@10':>8}{'MRR':>6}{'nDCG':>6}"
    f"{'en@5':>6}{'ja@5':>6}{'cross@5':>9}"
)
for size, overlap in [(200, 30), (400, 60), (800, 100)]:
    chunks = chunk_corpus(pages, size, overlap)
    for mode in "ABC":
        retrieve = Bm25Retriever(chunks, mode)
        at5 = evaluate(dev, retrieve, k=5)
        at10 = evaluate(dev, retrieve, k=10)
        total, by_lang, by_type = summarize(at5)["all"], summarize(at5, "lang"), summarize(at5, "type")
        low, high = total["hit_ci"]
        cross = by_type.get("cross-lingual", {"hit": float("nan")})["hit"]
        print(
            f"{size}/{overlap:<8}{mode:<5}{total['hit']:>7.2f}{f'({low:.2f}-{high:.2f})':>14}"
            f"{summarize(at10)['all']['hit']:>8.2f}{summarize(at10)['all']['rr']:>6.2f}"
            f"{summarize(at10)['all']['ndcg']:>6.2f}{by_lang['en']['hit']:>6.2f}"
            f"{by_lang['ja']['hit']:>6.2f}{cross:>9.2f}"
        )