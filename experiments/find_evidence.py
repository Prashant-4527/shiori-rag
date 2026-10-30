"""Search every ingested page for a phrase. Use it to find and check gold evidence pages."""

import argparse

from shiori_rag.chunking import read_pages
from shiori_rag.normalize import search_form

parser = argparse.ArgumentParser()
parser.add_argument("query")
parser.add_argument("--docs", default="", help="only doc ids containing this text")
args = parser.parse_args()

needle = search_form(args.query).lower()
hits = 0
for page in read_pages():
    if args.docs not in page["doc_id"]:
        continue
    text = page["text_search"].lower()
    at = text.find(needle)
    if at == -1:
        continue
    hits += 1
    snippet = text[max(0, at - 50) : at + len(needle) + 50].replace("\n", " ")
    print(f"{page['doc_id']}  p{page['pdf_page']}  ...{snippet}...")
print(f"\n{hits} page(s) contain {needle!r}")
