# shiori-rag (栞)

Bilingual (Japanese / English) question answering over METI trade white papers, with page-level citations.

> Status: work in progress. Day 2 of a 30-day build.

## What it will do

- Answer questions asked in Japanese or English using only METI documents.
- Cite the document and page for every answer.
- Say "the documents do not contain this" when the evidence is missing.
- Measure every design choice on a fixed evaluation set (retrieval, answer quality, citations, latency, cost).

## Why "shiori"?

栞 means bookmark. Each answer points back to the page it came from.

## Repository layout

| Path | Contents |
|---|---|
| `src/shiori_rag/` | Package code |
| `tests/` | Tests |
| `scripts/` | Data download and manifest builder |
| `experiments/` | Throwaway experiments, including the naive v0 baseline |
| `docs/PROBLEM.md` | Problem statement, users, success metrics |
| `docs/decisions.md` | Architecture decision records |
| `docs/DATA_CARD.md` | What is in the corpus, licence terms, known issues |
| `data/manifest.csv` | Source, hash and licence record for every document |

## Setup

```powershell
uv sync
uv run pytest
uv run python scripts/download_meti.py
```

## Data and licence

The PDFs are not stored in this repository. METI documents are used under METI's terms of use; see `docs/DATA_CARD.md` for the details and the third-party content notes.
