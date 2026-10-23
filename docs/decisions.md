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
