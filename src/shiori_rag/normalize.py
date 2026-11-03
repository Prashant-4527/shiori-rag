"""Text clean-up rules. Pure functions, no I/O, easy to test."""

import re
import unicodedata

_CJK = r"\u3000-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff00-\uffef"
_IS_CJK = re.compile(f"[{_CJK}]")
_INVISIBLE = re.compile("[\u200b\u200c\u200d\u2060\ufeff\u00ad]")
_SPACES = re.compile(r"[ \t\u00a0\u3000]+")
_SPACES = re.compile(r"[ \t\u00a0\u3000]+")
_CJK_GAP = re.compile(rf"(?<=[{_CJK}]) +| +(?=[{_CJK}])")


def _is_cjk(char: str) -> bool:
    return bool(_IS_CJK.match(char))


def join_lines(lines: list[str]) -> str:
    """Join the visual lines of one paragraph into a single string.

    No space between Japanese characters, a single space between Latin words,
    and a trailing hyphen followed by a lowercase letter is a split word.
    """
    out = ""
    for line in (ln.strip() for ln in lines):
        if not line:
            continue
        if not out:
            out = line
        elif out.endswith("-") and line[0].islower() and out[-2:-1].isalpha():
            out = out[:-1] + line
        elif _is_cjk(out[-1]) or _is_cjk(line[0]):
            out += line
        else:
            out += " " + line
    return out


def clean_display(text: str) -> str:
    """Tidy text for showing to a person. Keeps the original characters."""
    text = _INVISIBLE.sub("", text)
    text = _SPACES.sub(" ", text)
    text = re.sub(r" *\n *", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def digit_share(text: str) -> float:
    """Share of characters that are digits. High values mark chart-label pages."""
    return sum(ch.isdigit() for ch in text) / max(len(text), 1)


def search_form(text: str) -> str:
    """NFKC, spaces collapsed, and no spaces next to Japanese characters.
    Never shown to users."""
    text = _SPACES.sub(" ", unicodedata.normalize("NFKC", text)).strip()
    return _CJK_GAP.sub("", text)
