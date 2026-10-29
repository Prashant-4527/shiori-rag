from shiori_rag.chunking import chunk_page, pack_sentences, split_long, split_sentences


def test_japanese_sentences_split_after_full_stop():
    text = "経済は成長した。しかし課題もある。"
    assert split_sentences(text, "ja") == ["経済は成長した。", "しかし課題もある。"]


def test_closing_quote_stays_with_its_sentence():
    assert split_sentences("彼は「行く。」と言った。", "ja") == [
        "彼は「行く。」",
        "と言った。",
    ]


def test_japanese_tail_without_full_stop_is_kept():
    assert split_sentences("第一部。国際経済", "ja") == ["第一部。", "国際経済"]


def test_english_split_ignores_abbreviation():
    text = "The U.S. current account is large. It rose in 2024."
    assert split_sentences(text, "en") == [
        "The U.S. current account is large.",
        "It rose in 2024.",
    ]


def test_pack_respects_max_size_and_overlaps():
    items = [
        (f"文{i}" * 3 + "。", False) for i in range(6)
    ]  # each item is 8 characters
    chunks = pack_sentences(items, max_size=20, overlap=8, length=len)
    assert all(sum(len(t) for t, _ in c) <= 20 for c in chunks)
    assert chunks[0][-1] == chunks[1][0]  # the last sentence is repeated


def test_split_long_cuts_between_words_and_loses_nothing():
    sentence = "国際経済秩序の転換期に増幅する不確実性と、サプライチェーン強靱化の重要性を分析した結果、多くの課題が明らかになった。"
    pieces = split_long(sentence, 30, "ja", len)
    assert "".join(pieces) == sentence
    assert max(len(p) for p in pieces) <= 30


def test_chunks_stay_on_one_page_and_cover_every_sentence():
    page = {
        "doc_id": "d",
        "corpus": "trade",
        "lang": "ja",
        "file": "d.pdf",
        "pdf_page": 7,
        "layout": "prose",
        "flags": [],
        "text": "一文目です。二文目です。三文目です。\n\n四文目です。五文目です。",
    }
    chunks = chunk_page(page, max_size=14, overlap=7)
    assert {c["pdf_page"] for c in chunks} == {7}
    joined = "".join(c["text"] for c in chunks)
    for sentence in [
        "一文目です。",
        "二文目です。",
        "三文目です。",
        "四文目です。",
        "五文目です。",
    ]:
        assert sentence in joined
    assert chunks[0]["chunk_id"] == "d:p007:c00"
