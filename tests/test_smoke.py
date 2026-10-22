from shiori_rag.config import PROJECT_ROOT, RAW_DIR


def test_project_root_has_pyproject():
    assert (PROJECT_ROOT / "pyproject.toml").exists()


def test_raw_dir_is_under_data():
    assert RAW_DIR.parent == PROJECT_ROOT / "data"
