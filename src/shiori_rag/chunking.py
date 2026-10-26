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

    return [m.surfave() for m in _sudachi().tokenize(text, tokenizer.Tokenizer.SplitMode.C)]