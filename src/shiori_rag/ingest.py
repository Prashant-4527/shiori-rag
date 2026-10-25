"""Turn the raw PDFs listed in the manifest into one JSON line per page."""

import csv
import json
from pathlib import Path

from shiori_rag.config import DATA_DIR, PROCESSED_DIR, RAW_DIR
from shiori_rag.extract import extract_pages
from shiori_rag.normalize import clean_display, digit_share, search_form

# Layout by the part name after the colon in pair_id.
LAYOUT = {
    "exec-summary": "prose",
    "p2-c3-s5_global-south-co-creation": "report",
    "overview-slides": "slides",
    "summary": "slides",
}
NEAR_EMPTY = 80  # fewer characters than this: a divider or cover page
CHART_HEAVY = 0.25  # more digits than this: a page of chart labels


def read_manifest():
    with (DATA_DIR / "manifest.csv").open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def ingest():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    for row in read_manifest():
        layout = LAYOUT[row["pair_id"].split(":")[1]]
        pages = extract_pages(
            RAW_DIR / row["filename"], drop_edges=(layout == "report")
        )
        for page in pages:
            display = clean_display(page.text)
            flags = []
            if len(display) < NEAR_EMPTY:
                flags.append("near_empty")
            if digit_share(display) > CHART_HEAVY:
                flags.append("chart_heavy")
            records.append(
                {
                    "doc_id": Path(row["filename"]).stem,
                    "corpus": row["corpus"],
                    "lang": row["lang"],
                    "file": row["filename"],
                    "pdf_page": page.pdf_page,
                    "layout": layout,
                    "text": display,
                    "text_search": search_form(display),
                    "n_chars": len(display),
                    "flags": flags,
                    "dropped_markers": page.dropped_markers,
                    "dropped_edge_lines": page.dropped_edge_lines,
                }
            )
    out = PROCESSED_DIR / "pages.jsonl"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return records, out


def main():
    records, out = ingest()
    print(f"{len(records)} pages written to {out}\n")
    print(
        f"{'document':<60}{'pages':>6}{'chars':>8}{'empty':>6}{'chart':>6}{'marks':>6}{'edges':>6}"
    )
    for doc_id in dict.fromkeys(r["doc_id"] for r in records):
        rs = [r for r in records if r["doc_id"] == doc_id]
        print(
            f"{doc_id[:58]:<60}{len(rs):>6}{sum(r['n_chars'] for r in rs):>8}"
            f"{sum('near_empty' in r['flags'] for r in rs):>6}"
            f"{sum('chart_heavy' in r['flags'] for r in rs):>6}"
            f"{sum(r['dropped_markers'] for r in rs):>6}"
            f"{sum(r['dropped_edge_lines'] for r in rs):>6}"
        )


if __name__ == "__main__":
    main()
