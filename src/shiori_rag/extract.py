"""Layout-aware page extraction with PyMuPDF."""

from dataclasses import dataclass
from pathlib import Path

import pymupdf

from shiori_rag.normalize import join_lines

SUPERSCRIPT = 1  # bit set in a span's flags for superscript text
EDGE = 0.07  # top and bottom 7% of the page hold running headers and page numbers


@dataclass
class PageText:
    pdf_page: int  # 1-based index inside the file (ADR-008)
    text: str  # paragraphs separated by a blank line
    dropped_markers: int  # footnote markers removed
    dropped_edge_lines: int  # header or footer lines removed


def extract_pages(path: Path, drop_edges: bool) -> list[PageText]:
    pages = []
    with pymupdf.open(str(path)) as doc:
        for number, page in enumerate(doc, start=1):
            height = page.rect.height
            paragraphs, markers, edge_lines = [], 0, 0
            for block in page.get_text("dict", sort=True)["blocks"]:
                lines = []
                for line in block.get("lines", []):
                    top, bottom = line["bbox"][1], line["bbox"][3]
                    pieces = []
                    for span in line["spans"]:
                        if (
                            span["flags"] & SUPERSCRIPT
                            and span["text"].strip().isdigit()
                        ):
                            markers += 1
                            continue
                        pieces.append(span["text"])
                    text = "".join(pieces).strip()
                    if not text:
                        continue
                    if drop_edges and (
                        bottom < height * EDGE or top > height * (1 - EDGE)
                    ):
                        edge_lines += 1
                        continue
                    lines.append(text)
                if lines:
                    paragraphs.append(join_lines(lines))
            pages.append(PageText(number, "\n\n".join(paragraphs), markers, edge_lines))
    return pages
