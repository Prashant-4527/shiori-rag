"""Turn text into search tokens. Japanese uses Sudachi, everything else uses plain words."""

import re
from functools import lru_cache

from shiori_rag.normalize import search_form

MODES = ("A", "B", "C")


@lru_cache(maxsize=1)
def _sudachi():
    from sudachipy import dictionary

    return dictionary.Dictionary().tokenizer()


def japanese_words(text: str, mode: str = "C") -> list[str]:
    from sudachipy import tokenizer

    split_mode = getattr(tokenizer.Tokenizer.SplitMode, mode)
    return [m.surface() for m in _sudachi().tokenize(text, split_mode)]


def tokenize(text: str, lang: str, mode: str = "C") -> list[str]:
    """Lower-cased tokens without whitespace or punctuation."""
    text = search_form(text).lower()
    if lang == "ja":
        words = japanese_words(text, mode)
        return [w for w in words if w.strip() and not re.fullmatch(r"[\W_]+", w)]
    return re.findall(r"\w+", text)