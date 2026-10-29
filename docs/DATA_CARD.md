# Data card: shiori-rag corpus

## 1. Purpose

The corpus is the set of documents the system may answer from. It is used to build the retrieval index and to write the evaluation questions. Nothing outside this set counts as evidence.

## 2. Contents

8 files, 213 pages, English and Japanese, all published by the Ministry of Economy, Trade and Industry (METI).

| File | Lang | Pages | Pair | Pair quality | URL checked |
|---|---|---:|---|---|---|
| `meti_trade_wp_2025_en_exec-summary.pdf` | en | 6 | exec-summary | full | index-page |
| `meti_trade_wp_2025_en_overview-slides.pdf` | en | 34 | overview-slides | near | index-page |
| `meti_trade_wp_2025_en_p2-c3-s5_global-south-co-creation.pdf` | en | 19 | p2-c3-s5_global-south-co-creation | full | no |
| `meti_trade_wp_2025_ja_exec-summary.pdf` | ja | 4 | exec-summary | full | index-page |
| `meti_trade_wp_2025_ja_overview-slides.pdf` | ja | 36 | overview-slides | near | index-page |
| `meti_trade_wp_2025_ja_p2-c3-s5_global-south-co-creation.pdf` | ja | 15 | p2-c3-s5_global-south-co-creation | full | index-page |
| `meti_trade_wp_2026_en_summary.pdf` | en | 42 | summary | partial | fetched |
| `meti_trade_wp_2026_ja_summary.pdf` | ja | 57 | summary | partial | no |

Corpus tag: every file is tagged `trade` in `data/manifest.csv` (ADR-007). Pair quality: `full` means the same sections in both languages, `near` means a few extra slides on one side, `partial` means one side is a shorter deck.

The English 2026 deck has 42 slides and the Japanese deck has 57. Content on the extra Japanese slides can only be found through the Japanese file.

## 3. Licence and obligations

- Sources reviewed on 2026-10-29: [METI Terms of Use](https://www.meti.go.jp/english/other/terms_of_use.html) and the [Digital Agency's Public Data License (Version 1.0), English translation](https://www.digital.go.jp/en/resources/open_data).
- METI requires source attribution. When content is edited or processed, also state that it has been processed and identify the actor; do not present processed content as though the Government of Japan created it. Third-party content may be excluded from METI's reuse terms and must be checked separately.
- Suggested source-and-processing notice: "Source: White Paper on International Economy and Trade [year], Ministry of Economy, Trade and Industry of Japan (METI), [source PDF URL] (accessed YYYY-MM-DD). Text extracted and processed by the Shiori-RAG project."
- Public-demo rule: cite the document and PDF page, link to the original, never host the PDFs, and do not display excerpts until the source terms and any third-party rights have been reviewed.

This is a project-level reading of the published terms, not legal advice. Re-check the terms before public release.

This is a reading of the terms, not legal advice.

## 4. Third-party content inside METI files

METI's terms exclude third-party material. Most charts credit outside data providers (IMF, UN Comtrade, OECD, CEIC, Global Trade Atlas, Eurostat, Marklines, and others). The per-file list is in the `third_party_notes` column of the manifest. The two executive summaries are text only.

Pre-demo rule: chart-heavy pages may be retained for internal retrieval experiments, but do not display their extracted text as public excerpts until third-party chart/data credits and relevant rights have been reviewed.

## 5. Excluded sources

- JETRO documents: JETRO's general terms allow downloading and printing for the site's intended purposes, and require prior written permission for other reproduction, publishing or distribution. A public demo that shows excerpts would exceed that. Excluded under ADR-006 unless written permission is obtained.

## 6. How the data was collected

Manual download from METI's English and Japanese white paper pages, then `scripts/download_meti.py` to name the files and record page counts and SHA-256 hashes. URLs were checked against METI's index pages on 2026-10-23. File sizes of five files match the sizes METI lists. The EN 2-3-5 file and the JA 2026 summary still need a browser check (`url_verified` = no).

## 7. Known issues

- `experiments/parser_results.csv` currently reports zero anchor hits for every parser/probe pair. It must not be used to select a parser until `experiments/parser_bakeoff.py` completes with valid matches.
- Printed page numbers differ from file page numbers. The Part II Chapter 3 Section 5 PDFs print page 276 (JA) and 337 (EN) on a file that has pages 1 to 19 (ADR-008).
- Footnote numbers are glued to words in the text layer ("later.344", "...グループ）345の").
- A running header and the printed page number appear inside the body text on every page of the section PDFs.
- pypdf puts a newline at every visual line end, including in the middle of Japanese words.
- The current parser benchmark is invalid: every parser misses every anchor in the selected probe set. Re-measure chart-heavy-page character counts after the probes are corrected; do not rely on the older 13,000-character claim.
- Section-divider slides contain almost no text (EN 2026 pp. 1 and 39, JA 2026 pp. 1 and 51).

## 8. Reproducing

```powershell
uv sync
uv run python scripts/download_meti.py
```

The raw PDFs live in `data/raw/` and are not committed. The manifest records the source URL, access date, page count, hash, licence text and third-party notes for each file.
