"""Compare Japanese tokenizers on the ingested corpus."""

import json
from collections import Counter

from fugashi import Tagger
from sudachipy import dictionary, tokenizer

from shiori_rag.config import PROCESSED_DIR

SPLIT = tokenizer.Tokenizer.SplitMode
sudachi = dictionary.Dictionary().tokenizer()
unidic = Tagger()

with (PROCESSED_DIR / "pages.jsonl").open(encoding="utf-8") as fh:
    pages = [json.loads(line) for line in fh]
paragraphs = [para for p in pages if p["lang"] == "ja" for para in p["text_search"].split("\n\n")]
print(f"{len(paragraphs)} Japanese paragraphs\n")


def sudachi_tokens(text, mode):
    return [m.surface() for m in sudachi.tokenize(text, mode)]


def unidic_tokens(text):
    return [w.surface for w in unidic(text)]


taggers = {
    "Sudachi A": lambda t: sudachi_tokens(t, SPLIT.A),
    "Sudachi B": lambda t: sudachi_tokens(t, SPLIT.B),
    "Sudachi C": lambda t: sudachi_tokens(t, SPLIT.C),
    "fugashi (UniDic)": unidic_tokens,
}

print(f"{'tokenizer':<18}{'tokens':>8}{'vocab':>8}{'1-char %':>10}{'avg len':>9}")
for name, fn in taggers.items():
    tokens = [tok for para in paragraphs for tok in fn(para) if tok.strip()]
    vocab = Counter(tokens)
    singles = sum(1 for t in tokens if len(t) == 1) / len(tokens)
    print(f"{name:<18}{len(tokens):>8}{len(vocab):>8}{singles:>10.1%}{sum(map(len, tokens)) / len(tokens):>9.2f}")

sentence = next(p for p in paragraphs if "経済産業" in p or "サプライチェーン" in p)[:60]
print(f"\nSample: {sentence}")
for name, fn in taggers.items():
    print(f"  {name:<18}{' | '.join(fn(sentence))}")

print("\nInflected verbs, Sudachi C: surface -> dictionary form")
for m in sudachi.tokenize("不確実性が高まっている。悪化した。", SPLIT.C):
    if m.part_of_speech()[0] in ("動詞", "形容詞"):
        print(f"  {m.surface()} -> {m.dictionary_form()}")