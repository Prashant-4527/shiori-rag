from shiori_rag.normalize import clean_display, digit_share, join_lines, search_form


def test_japanese_lines_join_without_space():
    lines = ["経済産業省は、国際経", "済秩序の変化を分析した。"]
    assert join_lines(lines) == "経済産業省は、国際経済秩序の変化を分析した。"


def test_english_lines_join_with_one_space():
    assert join_lines(["growth was", "solid in 2024."]) == "growth was solid in 2024."


def test_split_word_with_hyphen_is_rejoined():
    assert join_lines(["inter-", "national trade"]) == "international trade"


def test_real_compound_split_at_line_end_loses_its_hyphen():
    # Known trade-off: a line-end hyphen is ambiguous. We rejoin, so trade-off becomes tradeoff.
    assert join_lines(["The trade-", "off is clear."]) == "The tradeoff is clear."


def test_hyphen_before_capital_letter_is_kept():
    assert join_lines(["Asia-", "Pacific"]) == "Asia- Pacific"


def test_mixed_line_boundary_uses_cjk_rule():
    assert join_lines(["ASEAN", "での雇用"]) == "ASEANでの雇用"


def test_clean_display_removes_invisible_and_extra_space():
    assert clean_display("a\u200b  b\u00a0 c\n\n\n\nd") == "a b c\n\nd"


def test_search_form_normalizes_width():
    assert search_form("成長率は３．３％（２０２４年）") == "成長率は3.3%(2024年)"


def test_digit_share():
    assert digit_share("1234") == 1.0
    assert digit_share("") == 0.0
