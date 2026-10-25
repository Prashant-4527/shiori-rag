import re

import pytest

from shiori_rag.config import RAW_DIR
from shiori_rag.extract import extract_pages

EN = RAW_DIR / "meti_trade_wp_2025_en_p2-c3-s5_global-south-co-creation.pdf"
JA = RAW_DIR / "meti_trade_wp_2025_ja_exec-summary.pdf"


@pytest.mark.skipif(not EN.exists(), reason="corpus not downloaded")
def test_footnote_markers_and_page_furniture_are_removed():
    pages = extract_pages(EN, drop_edges=True)
    assert len(pages) == 19
    assert sum(p.dropped_markers for p in pages) > 0
    assert "later.344" not in pages[1].text


@pytest.mark.skipif(not JA.exists(), reason="corpus not downloaded")
def test_japanese_paragraphs_have_no_midword_line_breaks():
    pages = extract_pages(JA, drop_edges=False)
    assert not any(
        re.search(r"[\u3040-\u9fff]\n[\u3040-\u9fff]", p.text) for p in pages
    )
    assert [p.pdf_page for p in pages] == [1, 2, 3, 4]
