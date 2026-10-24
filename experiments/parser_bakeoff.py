"""compare PDF parsers on a hand-picked probe set."""
import csv
import json
import time

from shiori_rag.config import PROJECT_ROOT, RAW_DIR
from shiori_rag.parse_eval import (
    anchor_hits, cjk_line_breaks, glued_footnotes, junk_chars, repeated_lines,
)
from shiori_rag.parsers import PARSERS

EXP = PROJECT_ROOT / "experiments"
OUT_DIR = EXP / "out"
OUT_DIR.mkdir(exist_ok=True)
probes = json.loads((EXP / "probes.json").read_text(encoding="utf-8"))

cache = {}  # (filename, parser) -> (pages, seconds per page)


def parse_cached(filename, parser):
    key = (filename, parser)
    if key not in cache:
        start = time.perf_counter()
        pages = PARSERS[parser](RAW_DIR / filename)
        cache[key] = (pages, (time.perf_counter() - start) / max(len(pages), 1))
    return cache[key]


rows = []
for probe in probes:
    for parser in PARSERS:
        pages, sec_per_page = parse_cached(probe["file"], parser)
        text = pages[probe["page"] - 1]
        (OUT_DIR / f"{probe['id']}__{parser}.txt").write_text(text, encoding="utf-8")
        rows.append({
            "probe": probe["id"], "type": probe["type"], "parser": parser,
            "chars": len(text),
            "anchors": f"{anchor_hits(text, probe['anchors'])}/{len(probe['anchors'])}",
            "cjk_breaks": cjk_line_breaks(text),
            "glued_footnotes": glued_footnotes(text),
            "junk": junk_chars(text),
            "sec_per_page": round(sec_per_page, 3),
        })

with (EXP / "day3_results.csv").open("w", encoding="utf-8-sig", newline="") as fh:
    writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

for r in rows:
    print(f"{r['probe']:<18}{r['parser']:<16}{r['chars']:>7}  anchors {r['anchors']:<5}"
          f" cjk_br {r['cjk_breaks']:>4}  fn {r['glued_footnotes']:>2}  junk {r['junk']:>2}"
          f"  {r['sec_per_page']:>6}s/page")

print("\nRepeated lines (possible headers and footers), top 3 per file and parser:")
for filename in sorted({p["file"] for p in probes}):
    for parser in PARSERS:
        pages, _ = parse_cached(filename, parser)
        print(f"  {filename[:46]:<46} {parser:<15} {repeated_lines(pages)[:3]}")