"""Check that every probe anchor really appears on its probe page."""

import json

from shiori_rag.config import PROJECT_ROOT, RAW_DIR
from shiori_rag.parse_eval import squash
from shiori_rag.parsers import parse_pymupdf

probes = json.loads(
    (PROJECT_ROOT / "experiments" / "probes.json").read_text(encoding="utf-8")
)
cache = {}
bad = 0
for probe in probes:
    if probe["file"] not in cache:
        cache[probe["file"]] = [
            squash(t) for t in parse_pymupdf(RAW_DIR / probe["file"])
        ]
    pages = cache[probe["file"]]
    for anchor in probe["anchors"]:
        found = [i + 1 for i, text in enumerate(pages) if squash(anchor) in text]
        if probe["page"] not in found:
            bad += 1
            print(
                f"{probe['id']}: page {probe['page']}, anchor found on {found or 'NOWHERE'}: {anchor[:40]}"
            )
print("all anchors OK" if not bad else f"\n{bad} anchors need fixing")
