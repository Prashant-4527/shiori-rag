# ADR-001: Select METI and JETRO Public Documents as the Initial Corpus

- **Status:** Accepted, subject to document-level licensing and feasibility checks
- **Date:** 2026-10-20
- **Decision owners:** Prashant

## Context

The Japanese White Paper RAG Chatbot needs a document corpus that is authoritative, relevant to Japan, and suitable for evaluating retrieval-augmented generation (RAG).

The corpus selection affects the entire system. PDF structure determines parsing requirements, language affects retrieval and tokenization, and document content determines the evaluation questions. Licensing also determines whether the documents and extracted content can be used in a public demonstration.

The project aims to help users retrieve verifiable information from Japanese policy and trade-related documents, including when they ask questions in English.

The corpus should therefore support the following goals:

- Use official, primary-source material relevant to Japan.
- Evaluate retrieval from Japanese-language source text.
- Support English questions against Japanese documents.
- Verify answers against specific document pages.
- Demonstrate a realistic document-research use case relevant to a future METI internship application.

Matching Japanese and English versions of the same report would be useful for additional evaluation, but their availability must be verified rather than assumed.

## Options Considered

| Criterion | Wikipedia (Japanese and English) | arXiv papers | METI and JETRO documents |
|---|---|---|---|
| Source authority | Community-edited encyclopedia | Research papers and preprints | Official institutional publications |
| Parsing effort | Low to moderate for clean text dumps | Moderate; equations and two-column layouts can be difficult | Potentially high; long PDFs, tables, charts, and scanned pages |
| Language challenge | Japanese and English content available | Many papers are English-language | Japanese sources enable English-to-Japanese retrieval tests |
| Retrieval evaluation | Some answers may already be familiar to the language model | Familiarity with well-known papers can affect evaluation | Recent or less familiar reports can help test whether retrieval supplies the evidence |
| Page-level verification | Possible, but source structure varies | Possible, with layout-related challenges | Directly relevant to policy-report page citations |
| Project relevance | General-purpose knowledge retrieval | Scientific literature retrieval | Direct alignment with Japanese policy and trade research |
| Main limitation | Model memorization and community-edited content | Less direct alignment with the intended use case | Parsing complexity, document availability, and licensing require investigation |

## Decision

Use publicly accessible METI and JETRO documents as the initial target corpus.

Start with a small, curated collection of reports that can be inspected and evaluated reliably. Confirm document availability, publication metadata, text extractability, and applicable reuse terms before indexing each document.

Treat Japanese-language documents as the primary source material. Use corresponding English versions where suitable versions can be verified, but do not require every document to have a parallel translation.

## Rationale

1. **Primary sources:** Official institutional publications provide a direct source for the policy and trade information the project is intended to retrieve.
2. **Relevant use case:** The corpus reflects a realistic research task rather than a generic question-answering benchmark.
3. **Cross-lingual evaluation:** English questions against Japanese source passages test whether retrieval can bridge a language difference. Matching Japanese and English versions can provide additional evaluation opportunities when available.
4. **Verifiable answers:** Claims can be checked against original documents and page references.
5. **Retrieval evaluation:** Recent or less familiar documents can reduce the risk of relying on information the language model already knows. This risk will be tested rather than assumed to be absent.

## Trade-offs

- PDF parsing and preservation of page-level metadata may require additional engineering.
- Japanese technical terminology and cross-lingual retrieval may reduce search quality.
- Manual verification of answers and citations will take time.
- The initial corpus will be smaller than a general-purpose knowledge collection.
- Public accessibility does not automatically grant permission to redistribute documents or extracted content.
- The availability of matching Japanese and English versions is not guaranteed.

## Consequences

The implementation will:

- Preserve document identifiers, titles, publication dates where available, and page numbers.
- Keep chunk metadata separately from the FAISS vector index.
- Evaluate retrieval and answer generation independently.
- Include English questions against Japanese source material.
- Test unanswerable questions and unsupported-answer behavior.
- Record the provenance and applicable usage terms of every indexed document.
- Report actual evaluation results instead of presenting targets as achieved results.

## Revisit Conditions

Reconsider this decision if:

1. The relevant documents cannot be used under their applicable licensing terms.
2. PDF extraction quality is too poor to support reliable retrieval and page-level verification.
3. The selected reports do not provide enough material to construct a meaningful evaluation dataset.
4. The corpus is unsuitable for the intended demonstration or evaluation goals.

If only some documents are unsuitable, replace those documents before reconsidering the entire corpus.

## Validation Plan

Before implementing the complete RAG pipeline:

1. Identify a small set of candidate METI and JETRO reports.
2. Record their titles, URLs, publication dates, languages, page counts, and usage terms.
3. Inspect representative pages containing ordinary text, tables, charts, and any scanned content.
4. Verify whether matching English versions exist for selected Japanese reports.
5. Create a small set of answerable and unanswerable questions.
6. Confirm that the expected answers can be verified against the original pages.


# ADR-002: Use uv, Python 3.11 and ruff for the development environment

- **Status:** Accepted
- **Date:** 2026-10-20

## Context
The project must install the same way on any machine, and the code needs consistent linting and testing.

## Decision
Use uv for dependencies and the lockfile, Python 3.11, ruff for linting and formatting, and pytest for tests.

## Rationale
The lockfile makes the environment reproducible. One tool (ruff) replaces three. Python 3.11 is supported by every library in the plan.

## Trade-offs
uv is newer than pip, and some hosting platforms expect a requirements.txt.

## Revisit if
A deployment target cannot use uv. We can export a requirements file from the lockfile.

---

# ADR-003: Use a src layout, a tests folder, and an experiments folder for throwaway code

- **Status:** Accepted
- **Date:** 2026-10-20

## Context
Early scripts tend to become the product. We need a clear line between code that stays and code that teaches.

## Decision
Reusable code lives in `src/shiori_rag/` with tests in `tests/`. One-off experiments live in `experiments/` and are never imported by the package.

## Rationale
The src layout stops accidental imports from the working folder. Keeping the naive v0 as an experiment preserves the "before" half of the before-and-after story.

## Trade-offs
Slightly more structure for a small project.

## Revisit if
The experiments folder starts holding code the package needs. Move it into `src/` with tests.

---

# ADR-004: Define metrics before measuring anything

- **Status:** Accepted
- **Date:** 2026-10-20

## Context
Targets chosen after seeing results can be tuned to look good.

## Decision
Write the success metrics and provisional targets in `PROBLEM.md` first. Evaluate retrieval separately from answer generation. Report measured numbers even when they miss the targets.

## Rationale
Separate measurements show whether a bad answer came from retrieval or from the model.

## Trade-offs
Early targets are guesses and will be revised after the baseline.

## Revisit if
The baseline shows a metric is not meaningful. Record the change in a new ADR instead of editing the old one.

---

# ADR-005: Keep raw PDFs and secrets out of git

- **Status:** Accepted
- **Date:** 2026-10-20

## Context
The PDFs are large and carry licence conditions. API keys committed once stay in history.

## Decision
`data/raw/`, `data/processed/`, `.env` and index files are git-ignored. The manifest and data card are committed. `.env.example` lists variable names only.

## Rationale
Anyone can rebuild the corpus from the manifest. No credential can reach the repository.

## Trade-offs
Cloning the repo does not give you the data, so setup needs one extra command.

## Revisit if
Documents are small and clearly redistributable.

---

# ADR-006: Use METI-hosted documents only for the public corpus

- **Status:** Accepted. Partially supersedes ADR-001.
- **Date:** 2026-10-23

## Context
ADR-001 selected METI and JETRO documents, subject to licence checks. The checks found a difference. METI's terms allow use under the Public Data License 1.0 with exceptions for third-party material. JETRO's general terms allow downloading and printing for the site's purposes and require written permission for other reproduction, publishing or distribution.

## Decision
The public corpus contains METI-hosted documents only. JETRO documents are excluded unless written permission is obtained. Third-party content inside METI files is recorded per file in the manifest.

## Rationale
A public demo that shows excerpts is publishing content. Only METI's terms clearly allow that, with attribution.

## Trade-offs
A smaller corpus and one publisher. This is a reading of the terms, not legal advice.

## Revisit if
JETRO grants written permission, or either site changes its terms.

---

# ADR-007: Build the pipeline to be domain-agnostic

- **Status:** Proposed
- **Date:** 2026-10-23

## Context
Most host companies for a METI internship are product and AI companies, and a pipeline tied to trade policy would look narrow.

## Decision
Every document carries a `corpus` tag. Nothing in the code refers to trade. The trade corpus comes first. A second, industry-facing corpus is added after its licence is checked. Each corpus gets its own evaluation questions and its own results table.

## Rationale
Running the same pipeline on two domains tests whether settings such as chunk size generalize.

## Trade-offs
More licence checks and more questions to write and verify.

## Revisit if
No suitable second corpus has a usable licence.

---

# ADR-008: Cite the PDF page index, not the printed page number

- **Status:** Accepted
- **Date:** 2026-10-23

## Context
The section PDFs carry the printed page of the full white paper (276 in the Japanese file, 337 in the English file) while the files themselves have pages 1 to 19. The two languages print different numbers.

## Decision
A citation means the 1-based page index inside the cited file. The printed page number may be stored as extra metadata, never as the citation.

## Rationale
A page index always opens the right page in the file, in both languages.

## Trade-offs
Users see "page 3 of this file", which differs from the printed number.

## Revisit if
We ingest the full white paper as one file, where printed and file numbers can be mapped.


# ADR-009: Use PyMuPDF Structured Extraction as the Initial PDF Processing Baseline

- **Status:** Proposed
- **Date:** 2026-10-28
- **Decision owner:** Prashant

## Context

Shiori-RAG processes Japanese and English METI publications in several PDF layouts, including prose documents, two-column reports, presentation slides, and chart-heavy pages.

The extraction pipeline must do more than retrieve text. It must preserve PDF page boundaries, maintain useful reading order, handle Japanese text without breaking words at visual line endings, and retain reliable document and page metadata for citations.

The project initially compared four PDF text-extraction implementations:

- `pypdf`
- `pdfplumber`
- PyMuPDF using `page.get_text("text")`
- PyMuPDF using `page.get_text("text", sort=True)`

These alternatives were evaluated using selected pages and checks for expected text anchors, Japanese line breaks, glued footnote markers, suspicious characters, and extraction time.

However, the parser benchmark must be validated before its results can establish a winner. If expected text anchors do not match, the comparison cannot reliably measure extraction quality.

## Decision

Use PyMuPDF's structured extraction as the initial production baseline while completing the comparative evaluation.

The implementation in `src/shiori_rag/extract.py` uses `page.get_text("dict", sort=True)` to access blocks, lines, spans, and their bounding boxes.

This enables the pipeline to:

1. Preserve one extracted text record per PDF page.
2. inspect the spatial position of lines.
3. remove numeric superscript markers identified through span flags.
4. optionally remove lines near the top and bottom margins of report pages.
5. normalize visual line breaks while preserving Japanese text continuity.
6. retain the original PDF page index for downstream citations.

The simpler parser implementations remain available in `src/shiori_rag/parsers.py` for benchmarking.

The current implementation is a baseline, not a claim that PyMuPDF has been proven superior for every document layout.

## Rationale

A structured extraction interface exposes layout information that is useful for handling recurring headers, footnote markers, and page-edge content.

This is particularly valuable for Shiori because its corpus contains both Japanese and English documents, and poor extraction can damage retrieval quality before embeddings or the language model are involved.

Keeping alternative parsers available also makes it possible to revisit the choice using reproducible measurements rather than intuition.

## Validation Requirements

Before accepting this decision, the parser benchmark must:

- Use valid, verified page numbers and expected text anchors.
- Report meaningful anchor-hit results for each probe.
- Include prose, two-column reports, slides, chart-heavy pages, and pages with footnotes.
- Compare reading order, Japanese line breaks, unwanted text, and extraction speed.
- Inspect the extracted text against the corresponding original PDF pages.
- Document known failures rather than treating character count as a measure of correctness.

The benchmark results must be regenerated from the corrected probes and saved consistently to `experiments/parser_results.csv`.

## Trade-offs

- Structured extraction provides access to layout information but requires more implementation and testing than a simple text-extraction call.
- Reading-order sorting does not guarantee perfect reconstruction of every multi-column page or complex slide.
- Superscript-marker removal relies on PDF formatting metadata and may require additional validation.
- Margin-based filtering can remove legitimate content if a document uses an unusual page layout.
- No text-based parser can guarantee accurate interpretation of every chart, table, or scanned page.

## Revisit If

- The corrected benchmark shows that another extraction strategy performs materially better on the fixed probe set.
- New document layouts expose systematic extraction failures.
- Page-level citation accuracy is compromised by extraction or page-number handling.

Any change to the selected extraction strategy should be supported by recorded benchmark results and regression tests.



# ADR-010: Preserve Page-Level Ingestion Records and Flag Potentially Noisy Pages

- **Status:** Accepted
- **Date:** 2026-10-28
- **Decision owner:** Prashant

## Context

Shiori-RAG ingests Japanese and English METI publications with different document layouts and text characteristics.

The corpus includes prose, presentation slides, section reports, chart-heavy pages, running headers, footers, and numeric superscript markers. These characteristics can introduce noise into the retrieval index or cause the system to overlook useful evidence.

The ingestion pipeline therefore needs to preserve page-level provenance while identifying pages that may be unsuitable for ordinary text-based retrieval.

The current corpus contains eight PDF files and 213 pages.

A recorded ingestion run produced the following aggregate results:

| Measurement | Result |
|---|---:|
| PDF documents | 8 |
| PDF pages processed | 213 |
| Extracted display-text characters | 299,495 |
| Pages flagged as near-empty | 3 |
| Pages flagged as chart-heavy | 24 |
| Removed numeric superscript markers | 25 |
| Removed top- or bottom-edge lines | 64 |

These are operational measurements from the current corpus and configuration, not independent measures of extraction accuracy.

## Decision

Represent ingestion output as one JSONL record per PDF page in `data/processed/pages.jsonl`.

Each record must retain document and provenance information, including:

- Document identifier and source filename.
- Corpus identifier and language.
- PDF page index.
- Layout classification.
- Display text and normalized search text.
- Character count and quality flags.
- Counts of removed superscript markers and edge lines.

Continue using layout-specific extraction and normalization rules.

The initial layout mapping is:

- Executive summaries: `prose`
- Section reports: `report`
- Overview slides and summaries: `slides`

Apply the existing quality flags as follows.

### Near-empty pages

A page with fewer than 80 display-text characters receives the `near_empty` flag.

Keep these page records in the processed output for traceability and debugging, but exclude them from chunk generation because covers and section-divider slides are unlikely to provide useful textual evidence.

### Chart-heavy pages

A page whose digit share exceeds 0.25 receives the `chart_heavy` flag.

Retain these pages and their flags in the processed data. Do not treat the flag as proof that a page is unusable.

The current chunking pipeline carries this flag forward. Before a public demo displays excerpts from chart-heavy chunks, the application must apply an explicit content-display policy that accounts for extraction quality and third-party material restrictions recorded in `docs/DATA_CARD.md`.

### Page-edge filtering

Apply the existing top- and bottom-edge filtering only to the `report` layout, where recurring headers and printed page numbers have been observed.

Keep edge filtering disabled for the other layouts until their extraction behavior justifies a different policy.

### Page citations

Retain the one-based PDF page index as the citation page number, following ADR-008. Ingestion and normalization must not merge page boundaries or replace PDF page indexes with printed page numbers.

## Rationale

Page-level records make the ingestion pipeline auditable and reproducible. They allow extraction failures to be traced to a specific source file and page without losing provenance during normalization or chunking.

Quality flags separate detection from filtering. This avoids permanently discarding potentially useful material based on simple heuristics before its value has been evaluated.

Layout-specific rules also reduce the risk of applying report-specific assumptions to presentation slides or prose documents.

## Trade-offs

- The 80-character near-empty threshold is heuristic and may classify some useful pages incorrectly.
- Digit share is an imperfect indicator of chart-heavy content. A page can contain a chart without exceeding the threshold, or contain many digits without being chart noise.
- A fixed margin threshold can remove legitimate content from documents with unusual layouts.
- Keeping noisy pages in the processed corpus requires downstream components to respect their flags where appropriate.
- Preserving page-level metadata increases the amount of data stored but supports traceability and citation verification.

## Validation and Reproducibility

The current ingestion run establishes a baseline of eight documents, 213 PDF pages, and 299,495 extracted characters.

Future changes should verify that:

1. Page counts match the manifest and source files.
2. Each processed record points to the correct filename and one-based PDF page.
3. Quality flags are computed consistently from the display text.
4. Removed-marker and edge-line counts are recorded for inspection.
5. Normalization preserves Japanese text continuity and intended paragraph boundaries.
6. Chart-heavy and near-empty pages are handled according to their documented policies.
7. The ingestion tests pass after changes to extraction or normalization.

The following commands reproduce the ingestion workflow after downloading the source PDFs:

```powershell
uv run python scripts/download_meti.py
uv run pytest
uv run python -m shiori_rag.ingest
```

## Revisit If

- The document corpus expands to additional layouts or publishers.
- Manual inspection reveals recurring false positives or false negatives in the page flags.
- Evaluation shows that chart-heavy pages improve retrieval when processed with a different strategy.
- Extraction changes affect page-level citation correctness or the recorded ingestion baseline.