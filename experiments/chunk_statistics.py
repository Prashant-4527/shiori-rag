"""Compare chunk settings on the ingested pages, measured in tokens."""

import statistics as st
from functools import cache

from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer

from shiori_rag.chunking import chunk_corpus, read_pages

tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3")
END = tuple("。！？!?.」）)]】")


@cache
def tokens(text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))


def summary(label, sizes_by_lang, ends):
    allsizes = sorted(s for sizes in sizes_by_lang.values() for s in sizes)
    n = len(allsizes)
    per_lang = {lang: round(st.mean(sizes)) for lang, sizes in sizes_by_lang.items()}
    print(
        f"{label:<24}{n:>7}{st.median(allsizes):>8.0f}{allsizes[int(n * 0.95)]:>7}{max(allsizes):>7}"
        f"{100 * sum(ends) / n:>8.0f}%   mean tokens by language: {per_lang}"
    )


pages = read_pages()
print(f"{'config (tokens)':<24}{'chunks':>7}{'median':>8}{'p95':>7}{'max':>7}{'clean':>9}")
for size, overlap in [(128, 16), (256, 32), (512, 64)]:
    chunks = chunk_corpus(pages, size, overlap, length=tokens)
    by_lang = {}
    for c in chunks:
        by_lang.setdefault(c["lang"], []).append(c["size"])
    summary(
        f"sentence-aware {size}/{overlap}",
        by_lang,
        [c["text"].rstrip().endswith(END) for c in chunks],
    )

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
by_lang, ends = {}, []
for page in pages:
    if "near_empty" in page["flags"]:
        continue
    for text in splitter.split_text(page["text"]):
        by_lang.setdefault(page["lang"], []).append(tokens(text))
        ends.append(text.rstrip().endswith(END))
summary("naive splitter 500/50ch", by_lang, ends)