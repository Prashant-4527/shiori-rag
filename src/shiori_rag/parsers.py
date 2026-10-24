"""Thin wrappers so every PDF parser looks the same: path -> list of page texts."""
from collections.abc import Callable
from pathlib import Path

PageTexts = list[str]  # index 0 is PDF page 1


def parse_pypdf(path: Path) -> PageTexts:
    from pypdf import PdfReader

    return [(page.extract_text() or "") for page in PdfReader(path).pages]


def parse_pdfplumber(path: Path) -> PageTexts:
    import pdfplumber

    with pdfplumber.open(path) as pdf:
        return [(page.extract_text() or "") for page in pdf.pages]


def parse_pymupdf(path: Path) -> PageTexts:
    import pymupdf

    with pymupdf.open(str(path)) as doc:
        return [page.get_text("text") for page in doc]


def parse_pymupdf_sorted(path: Path) -> PageTexts:
    import pymupdf

    with pymupdf.open(str(path)) as doc:
        return [page.get_text("text", sort=True) for page in doc]


PARSERS: dict[str, Callable[[Path], PageTexts]] = {
    "pypdf": parse_pypdf,
    "pdfplumber": parse_pdfplumber,
    "pymupdf": parse_pymupdf,
    "pymupdf_sorted": parse_pymupdf_sorted,
}