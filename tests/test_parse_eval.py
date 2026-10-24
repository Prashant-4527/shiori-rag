import pytest

from shiori_rag.config import RAW_DIR
from shiori_rag.parse_eval import anchor_hits, glued_footnotes, repeated_lines
from shiori_rag.parsers import PARSERS


def test_anchor_survives_line_breaks_and_width_differences():
    page = "2024 年の世界経済は 3.3％の\n底堅い成長だった"
    assert anchor_hits(page, ["2024年の世界経済は3.3%の底堅い成長"]) == 1


def test_anchor_fails_when_order_is_scrambled():
    page = "底堅い成長だった 2024年の世界経済は"
    assert anchor_hits(page, ["2024年の世界経済は底堅い成長だった"]) == 0


def test_empty_anchor_is_rejected():
    with pytest.raises(ValueError):
        anchor_hits("text", [""])


def test_glued_footnotes_detected_in_both_languages():
    assert glued_footnotes("a few years later.344 For") == 1
    assert glued_footnotes("ワーキンググループ）345の設置") == 1


def test_repeated_lines_masks_page_numbers():
    pages = [f"Header\nbody {i}\n{270 + i}" for i in range(4)]
    found = dict(repeated_lines(pages))
    assert found["Header"] == 4
    assert found["#"] == 4


PDF = RAW_DIR / "meti_trade_wp_2025_ja_exec-summary.pdf"


@pytest.mark.skipif(not PDF.exists(), reason="corpus not downloaded")
@pytest.mark.parametrize("name", list(PARSERS))
def test_every_parser_returns_one_text_per_page(name):
    pages = PARSERS[name](PDF)
    assert len(pages) == 4
    assert sum(len(p) for p in pages) > 1000