"""Sentence-aware chunking. A chunk never crosses a page (ADR-008)."""

import json
import re
from collections.abc import Callable
from functools import lru_cache

from shiori_rag.config import PROCESSED_DIR
from shiori_rag.normalize import search_form

# Japanese: a sentence ends at 。！？ (plus closing brackets). The last alternative keeps the tail.
_JA_SENTENCE = re.compile(r"[^。！？]*[。！？]+[」』）)]*|[^。！？]+")
# English: split after . ! ? before a capital letter, but not after "U." in "U.S."
_EN_SPLIT = re.compile(r"(?<![A-Z]\.)(?<=[.!?])\s+(?=[A-Z\[(\"“])")

Length = Callable[[str], int]


@lru_cache(maxsize=1)
def _sudachi():
    from sudachipy import dictionary

    return dictionary.Dictionary().tokenizer()


def japanese_words(text: str) -> list[str]:
    from sudachipy import tokenizer

    return [m.surface() for m in _sudachi().tokenize(text, tokenizer.Tokenizer.SplitMode.C)]


def split_sentences(paragraph: str, lang: str) -> list[str]:
    if lang == "ja":
        parts = _JA_SENTENCE.findall(paragraph)
    else:
        parts = _EN_SPLIT.split(paragraph)
    return [p.strip() for p in parts if p.strip()]


def split_long(sentence: str, max_size: int, lang: str, length: Length) -> list[str]:
    """Last resort for a sentence longer than max_size: cut it between words, never inside one."""
    words, glue = (japanese_words(sentence), "") if lang == "ja" else (sentence.split(" "), " ")
    pieces, current = [], ""
    for word in words:
        candidate = current + glue + word if current else word
        if current and length(candidate) > max_size:
            pieces.append(current)
            current = word
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces


def pack_sentences(items: list[tuple[str, bool]], max_size: int, overlap: int, length: Length):
    """Group (sentence, starts_paragraph) items into chunks of at most max_size.

    The last sentences of a chunk (up to `overlap` in size) are repeated at the start of the next one.
    """
    chunks, current, size = [], [], 0
    for item in items:
        n = length(item[0])
        if current and size + n > max_size:
            chunks.append(current)
            keep, kept = [], 0
            for prev in reversed(current):
                if kept + length(prev[0]) > overlap:
                    break
                keep.insert(0, prev)
                kept += length(prev[0])
            while keep and kept + n > max_size:
                kept -= length(keep.pop(0)[0])
            current, size = keep, kept
        current.append(item)
        size += n
    if current:
        chunks.append(current)
    return chunks


def render(chunk: list[tuple[str, bool]], lang: str) -> str:
    glue = "" if lang == "ja" else " "
    out = ""
    for index, (text, new_paragraph) in enumerate(chunk):
        if index == 0:
            out = text
        elif new_paragraph:
            out += "\n" + text
        else:
            out += glue + text
    return out


def chunk_page(page: dict, max_size: int, overlap: int, length: Length = len) -> list[dict]:
    lang = page["lang"]
    items, hard_split = [], 0
    for paragraph in page["text"].split("\n\n"):
        first = True
        for sentence in split_sentences(paragraph, lang):
            pieces = (
                split_long(sentence, max_size, lang, length)
                if length(sentence) > max_size
                else [sentence]
            )
            hard_split += len(pieces) > 1
            for piece in pieces:
                items.append((piece, first))
                first = False
    records = []
    for index, chunk in enumerate(pack_sentences(items, max_size, overlap, length)):
        text = render(chunk, lang)
        flags = [f for f in page["flags"] if f == "chart_heavy"]
        if hard_split:
            flags.append("hard_split")
        records.append(
            {
                "chunk_id": f"{page['doc_id']}:p{page['pdf_page']:03d}:c{index:02d}",
                "doc_id": page["doc_id"],
                "corpus": page["corpus"],
                "lang": lang,
                "file": page["file"],
                "pdf_page": page["pdf_page"],
                "layout": page["layout"],
                "text": text,
                "text_search": search_form(text),
                "size": length(text),
                "flags": flags,
            }
        )
    return records


def chunk_corpus(pages: list[dict], max_size: int, overlap: int, length: Length = len):
    chunks = []
    for page in pages:
        if "near_empty" in page["flags"]:
            continue  # covers and divider slides hold no evidence
        chunks.extend(chunk_page(page, max_size, overlap, length))
    return chunks


def read_pages() -> list[dict]:
    with (PROCESSED_DIR / "pages.jsonl").open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


def main(max_size: int = 400, overlap: int = 60) -> None:
    chunks = chunk_corpus(read_pages(), max_size, overlap)
    out = PROCESSED_DIR / "chunks.jsonl"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for chunk in chunks:
            fh.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"{len(chunks)} chunks written to {out}")


if __name__ == "__main__":
    main()