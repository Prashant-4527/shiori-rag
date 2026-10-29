"""compare PDF parsers on a hand-picked probe set."""

import csv
import json
import time

from shiori_rag.config import PROJECT_ROOT, RAW_DIR
from shiori_rag.parse_eval import (
    anchor_hits,
    cjk_line_breaks,
    glued_footnotes,
    junk_chars,
    repeated_lines,
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
        rows.append(
            {
                "probe": probe["id"],
                "type": probe["type"],
                "parser": parser,
                "chars": len(text),
                "anchors": f"{anchor_hits(text, probe['anchors'])}/{len(probe['anchors'])}",
                "cjk_breaks": cjk_line_breaks(text),
                "glued_footnotes": glued_footnotes(text),
                "junk": junk_chars(text),
                "sec_per_page": round(sec_per_page, 3),
            }
        )

# Fail closed: a probe with zero anchor matches for every parser is invalid
# evidence for comparing parsers. Diagnose whether the page is wrong or the anchors
# are absent from the source PDF before allowing a new CSV to be written.
invalid_probes = []
for probe in probes:
    scores = {}
    elsewhere = {}
    for parser in PARSERS:
        pages, _ = parse_cached(probe["file"], parser)
        target_text = pages[probe["page"] - 1] if probe["page"] <= len(pages) else ""
        hits = anchor_hits(target_text, probe["anchors"])
        scores[parser] = f"{hits}/{len(probe['anchors'])}"
        if hits == 0:
            page_hits = [
                (page_no, anchor_hits(text, probe["anchors"]))
                for page_no, text in enumerate(pages, start=1)
            ]
            page_hits = [(page_no, count) for page_no, count in page_hits if count > 0]
            if page_hits:
                best = sorted(page_hits, key=lambda item: (-item[1], item[0]))[:3]
                elsewhere[parser] = ", ".join(
                    f"p.{page_no}={count}/{len(probe['anchors'])}"
                    for page_no, count in best
                )
    if not any(int(score.split("/", maxsplit=1)[0]) > 0 for score in scores.values()):
        invalid_probes.append((probe, scores, elsewhere))

if invalid_probes:
    details = []
    for probe, scores, elsewhere in invalid_probes:
        details.append(
            f"  - {probe['id']} (configured page {probe['page']}): "
            + ", ".join(f"{parser}={score}" for parser, score in scores.items())
        )
        if elsewhere:
            details.extend(
                f"      {parser} has anchor hits elsewhere: {pages}"
                for parser, pages in elsewhere.items()
            )
        else:
            details.append(
                "      No configured anchor was found on any page; re-check the "
                "probe text and source PDF."
            )
    raise SystemExit(
        "ERROR: refusing to write experiments/parser_results.csv because one or "
        "more probes have zero anchor hits across every parser.\n"
        + "\n".join(details)
        + "\n\nInspect experiments/out/<probe>__<parser>.txt, correct the page "
        "or anchors in experiments/probes.json, and rerun the benchmark. The old "
        "CSV has been left untouched and must not be treated as a valid comparison."
    )

with (EXP / "parser_results.csv").open(
    "w", encoding="utf-8-sig", newline=""
) as fh:
    writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

for r in rows:
    print(
        f"{r['probe']:<18}{r['parser']:<16}{r['chars']:>7}  anchors {r['anchors']:<5}"
        f" cjk_br {r['cjk_breaks']:>4}  fn {r['glued_footnotes']:>2}  junk {r['junk']:>2}"
        f"  {r['sec_per_page']:>6}s/page"
    )

print("\nRepeated lines (possible headers and footers), top 3 per file and parser:")
for filename in sorted({p["file"] for p in probes}):
    for parser in PARSERS:
        pages, _ = parse_cached(filename, parser)
        print(f"  {filename[:46]:<46} {parser:<15} {repeated_lines(pages)[:3]}")
