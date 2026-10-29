# shiori-rag (栞)

Bilingual Japanese / English question answering over METI trade white papers, designed to return page-level citations and abstain when the corpus lacks evidence.

> **Status:** Research prototype in progress. The parser benchmark and naive baseline are not validated yet; do not treat the current parser scores as a result.

## Project milestones

- [x] Curate a small METI-only document corpus and record file provenance in `data/manifest.csv`.
- [x] Implement page-level PDF extraction, normalization, and chunking modules.
- [ ] Revalidate the anchors in `experiments/probes.json` against the local source PDFs, then rerun the parser bake-off.
- [ ] Record the naive v0 baseline on the Japanese executive summary and overview slides.
- [ ] Run chunk-size statistics and record measured results before making ADR-011.
- [ ] Document parser failure cases after the benchmark has valid anchor matches.
- [ ] Verify all source URLs marked `no` and finish source-specific reuse review.
- [ ] Evaluate retrieval, citations, answer correctness, abstention, latency, and cost on a fixed question set.
- [ ] Run the test suite and lint/format checks on the final working tree.

## What it aims to do

- Answer questions in Japanese or English using only the selected METI documents.
- Cite the source document and PDF page for every evidence-backed answer.
- Say when the documents do not contain enough evidence.
- Measure design choices on a fixed evaluation set instead of assuming a component is effective.

## Why "shiori"?

栞 means bookmark. Each answer should point back to the page it came from.

## Repository layout

| Path | Contents |
|---|---|
| `src/shiori_rag/` | Package code for extraction, normalization, ingestion, and chunking |
| `tests/` | Unit and smoke tests |
| `scripts/` | Document downloads and manifest generation |
| `experiments/` | Parser comparison, chunk statistics, tokenization experiments, and naive v0 baseline |
| `docs/PROBLEM.md` | Problem definition, target users, and success metrics |
| `docs/decisions.md` | Architecture decision records |
| `docs/DATA_CARD.md` | Corpus, provenance, licensing notes, and known limitations |
| `data/manifest.csv` | Source URL, hash, page count, licence, and provenance record for each document |

## Setup

Run from the repository root in PowerShell:

```powershell
uv sync
uv run python scripts/download_meti.py
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Experiments

After the source PDFs are available in `data/raw/`:

```powershell
uv run python experiments/parser_bakeoff.py
uv run python experiments/chunk_statistics.py
uv run python experiments/v0_naive.py data/raw/meti_trade_wp_2025_ja_exec-summary.pdf
uv run python experiments/v0_naive.py data/raw/meti_trade_wp_2025_ja_overview-slides.pdf
```

The parser bake-off refuses to update `experiments/parser_results.csv` if any probe has zero anchor hits across all parsers. Inspect its per-parser text files in `experiments/out/`, correct the page or anchors in `experiments/probes.json`, and rerun it.

## Data and licence

PDFs are not committed to this repository; download them from their source URLs. The public corpus is limited to METI-hosted documents unless separate permission is obtained. Read `docs/DATA_CARD.md` before displaying excerpts, especially from chart-heavy pages containing third-party material.
