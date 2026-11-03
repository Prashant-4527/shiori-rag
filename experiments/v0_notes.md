# Naive baseline (v0)

**Status: pending local run.** The source PDFs are not committed to the repository, and no retrieval or answer-quality measurements are recorded here yet. Do not describe v0 as evaluated until both runs and the question tables are complete.

## 1. Run the two baseline documents

Run from the repository root after `data/raw/` contains the PDFs:

```powershell
uv run python experiments/v0_naive.py data/raw/meti_trade_wp_2025_ja_exec-summary.pdf
uv run python experiments/v0_naive.py data/raw/meti_trade_wp_2025_ja_overview-slides.pdf
```

The script requires Ollama to be running with the configured model (default `qwen3:4b`) and loads the `BAAI/bge-m3` embedding model. Record the model names and environment used.

| Document | PDF pages | Chunks reported by script | Questions tested | Notes |
|---|---:|---:|---:|---|
| Japanese 2025 executive summary | 4 | pending | pending | Run locally |
| Japanese 2025 overview slides | 36 | pending | pending | Run locally |

## 2. Inspect retrieval behavior

For each document, ask the same five questions: two Japanese questions, two English questions, and one question the document cannot answer. Copy each question exactly so later versions can be compared fairly.

| # | Document | Language | Question | Expected evidence/page | Correct page in top 5? | Answer supported? | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Executive summary | Japanese | pending | pending | pending | pending | |
| 2 | Executive summary | English | pending | pending | pending | pending | |
| 3 | Executive summary | Japanese | pending | pending | pending | pending | |
| 4 | Executive summary | English | pending | pending | pending | pending | |
| 5 | Executive summary | Either | Unanswerable question | No supporting page | pending | pending | |
| 6–10 | Overview slides | JA/EN | Same five question types, tailored to this document | pending | pending | pending | |

## 3. Chunk inspection

The baseline script reports page and chunk counts but does not print random chunks. Inspect several source pages against the corresponding parser output in `experiments/out/`; do not claim this step is complete until the excerpts have been reviewed.

| Document/page | Starts mid-sentence? | Ends mid-sentence? | Header/footer/page-number noise? | Chart-label noise? | Notes |
|---|---|---|---|---|---|
| Pending local inspection | pending | pending | pending | pending | |

## 4. What failed

Complete from observed outputs, not expectations.

1. Pending local run.
2. Pending local run.
3. Pending local run.

## 5. Reproducibility record

- Commit SHA:
- Run date:
- OS / Python version:
- Ollama model and version:
- Embedding model:
- Source PDFs' SHA-256 values from `data/manifest.csv`:
- Command errors:
