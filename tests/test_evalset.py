from shiori_rag.evalset import load_questions, validate

PAGES = [{"doc_id": "d", "pdf_page": 1}, {"doc_id": "d", "pdf_page": 2}]


def make(**changes):
    base = {
        "id": "q1",
        "lang": "en",
        "type": "numeric",
        "question": "How much?",
        "answer": "3%",
        "answerable": True,
        "evidence": [{"pages": [{"doc_id": "d", "pdf_page": 1}]}],
        "origin": "hand",
        "verified": True,
        "split": "dev",
    }
    return {**base, **changes}


def test_valid_question_has_no_problems():
    assert validate([make()], PAGES) == []


def test_unknown_page_is_reported():
    bad = make(evidence=[{"pages": [{"doc_id": "d", "pdf_page": 9}]}])
    assert any("unknown page" in p for p in validate([bad], PAGES))


def test_unanswerable_must_have_no_evidence():
    bad = make(answerable=False, type="unanswerable")
    assert any("no evidence" in p for p in validate([bad], PAGES))
    ok = make(answerable=False, type="unanswerable", evidence=[])
    assert validate([ok], PAGES) == []


def test_duplicate_ids_and_bad_labels_are_reported():
    problems = validate([make(), make(lang="fr", split="train")], PAGES)
    assert any("duplicate id" in p for p in problems)
    assert any("lang" in p for p in problems)
    assert any("split" in p for p in problems)


def test_strict_mode_requires_verification():
    assert validate([make(verified=False)], PAGES) == []
    assert any(
        "not verified" in p
        for p in validate([make(verified=False)], PAGES, strict=True)
    )


def test_load_questions_reads_one_object_per_line(tmp_path):
    path = tmp_path / "q.jsonl"
    path.write_text('{"id": "a"}\n\n{"id": "b"}\n', encoding="utf-8")
    assert [q["id"] for q in load_questions(path)] == ["a", "b"]
