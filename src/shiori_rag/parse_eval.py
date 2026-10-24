"""Cheap checks for parser output. Smoke detectors, not ground truth."""
import re
import unicodedata
from collections import Counter


_CJK = r"\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff"
_CJK_BREAK = re.compile(rf"(?<=[{_CJK}])\n(?=[{_CJK}])")
_GLUED_EN = re.compile(r"(?<=[A-Za-z])[.,]\d{2,3}(?=\s|$)")
_GLUED_JA = re.compile(r"(?<=[）)」])\d{2,3}(?=[ぁ-んァ-ヶ一-龥])")
_JUNK = re.compile(r"\ufffd|\(cid:\d+\)")


def squash(text: str) -> str:
    """NFKC-normalize and delete all whitespace, so line breaks cannot hide a match."""
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text))


def anchor_hits(page_text: str, anchors: list[str]) -> int:
    """How many hand-copied sentences appear intact in the parser output."""
    if any(not a.strip() for a in anchors):
        raise ValueError("empty anchor: an empty string matches everything")
    squashed = squash(page_text)
    return sum(squash(a) in squashed for a in anchors)


def cjk_line_breaks(text: str) -> int:
    return len(_CJK_BREAK.findall(text))



def glued_footnotes(text: str) -> int:
    return len(_GLUED_EN.findall(text)) + len(_GLUED_JA.findall(text))


def junk_chars(text: str) -> int:
    return len(_JUNK.findall(text))


def repeated_lines(pages: list[str], min_share: float = 0.5) -> list[tuple[str, int]]:
    """Lines that repeat across pages (headers, footers). Digits are masked so page numbers match."""
    counts: Counter[str] = Counter()

    for page in pages:
        seen = {re.sub(r"\d+", "#", line.strip()) for line in page.splitlines() if line.strip()}
        counts.update(seen)
    cutoff = max(2, int(len(pages) * min_share))
    return [(line, n) for line, n in counts.most_common() if n >= cutoff]



