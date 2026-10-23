# v0 notes (naive RAG)

Run 1: data/raw/meti_trade_wp_2025_ja_exec-summary.pdf (4 pages, clean prose)
Run 2: data/raw/meti_trade_wp_2025_ja_overview-slides.pdf (36 pages, chart-heavy slides)

## Chunk inspection
Print 10 random chunks. For each, mark: starts mid-sentence? ends mid-sentence? contains header, footer or page number? contains chart-label soup?

| # | page | starts mid-sentence | ends mid-sentence | junk (header/footer/labels) |
|---|---|---|---|---|

## Questions (write your own after skimming the PDF)
| # | language | question | expected page | rank where correct page appeared | answer correct? | notes |
|---|---|---|---|---|---|---|

Include 2 Japanese, 2 English, and 1 question the document cannot answer.

## What failed, in my own words
1.
2.
3.

## What I will test tomorrow