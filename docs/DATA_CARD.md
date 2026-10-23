# Data card: shiori-rag corpus

> Draft written on Day 2. Read every line, check it against the sources, and rewrite it in your own words. Items marked TODO need a decision or a check from you.

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

- Source of terms: METI Terms of Use, https://www.meti.go.jp/english/other/terms_of_use.html. As read on 2026-10-22, content may be used if the Public Data License 1.0 (PDL 1.0) is followed. Some content is excluded, mainly third-party material.
- TODO: read PDL 1.0 and the exclusions list yourself. Write down exactly what we must show (attribution wording, a note when content is processed) and where the demo will show it.
- Working attribution, to confirm against PDL 1.0: "Source: Ministry of Economy, Trade and Industry (METI), White Paper on International Economy and Trade 2025 / 2026."
- Rule for the public demo (proposed): show short text excerpts with a document-and-page citation and a link to the original. Never host the PDFs.

This is a reading of the terms, not legal advice.

## 4. Third-party content inside METI files

METI's terms exclude third-party material. Most charts credit outside data providers (IMF, UN Comtrade, OECD, CEIC, Global Trade Atlas, Eurostat, Marklines, and others). The per-file list is in the `third_party_notes` column of the manifest. The two executive summaries are text only.

TODO: decide how the demo treats chart-label text. Proposal: index it for retrieval, but do not display chart-label chunks as excerpts.

## 5. Excluded sources

- JETRO documents: JETRO's general terms allow downloading and printing for the site's intended purposes, and require prior written permission for other reproduction, publishing or distribution. A public demo that shows excerpts would exceed that. Excluded under ADR-006 unless written permission is obtained.

## 6. How the data was collected

Manual download from METI's English and Japanese white paper pages, then `scripts/download_meti.py` to name the files and record page counts and SHA-256 hashes. URLs were checked against METI's index pages on 2026-10-23. File sizes of five files match the sizes METI lists. The EN 2-3-5 file and the JA 2026 summary still need a browser check (`url_verified` = no).

## 7. Known issues (from inspection on Day 2)

- Printed page numbers differ from file page numbers. The Part II Chapter 3 Section 5 PDFs print page 276 (JA) and 337 (EN) on a file that has pages 1 to 19 (ADR-008).
- Footnote numbers are glued to words in the text layer ("later.344", "...グループ）345の").
- A running header and the printed page number appear inside the body text on every page of the section PDFs.
- pypdf puts a newline at every visual line end, including in the middle of Japanese words.
- Slides contain thousands of characters of chart labels. EN 2026 slide 30 and JA 2026 slide 40 each have more than 13,000 characters.
- Section-divider slides contain almost no text (EN 2026 pp. 1 and 39, JA 2026 pp. 1 and 51).

TODO: add what the Day 3 parser comparison finds.

## 8. Reproducing

```powershell
uv sync
uv run python scripts/download_meti.py
```

The raw PDFs live in `data/raw/` and are not committed. The manifest records the source URL, access date, page count, hash, licence text and third-party notes for each file.
