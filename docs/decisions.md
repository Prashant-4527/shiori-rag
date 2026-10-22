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


