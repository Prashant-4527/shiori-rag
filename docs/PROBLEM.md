# Problem

## 1. Background

METI and JETRO publish policy reports, white papers, trade analyses, and industry research related to Japan. These publications can contain hundreds of pages of Japanese text, tables, charts, and specialized terminology.

Readers may include policy analysts, researchers, students, international professionals, and companies investigating Japan's economy, industries, trade, and technology policies.

However, finding reliable answers in these documents can be difficult, particularly for readers who are unfamiliar with Japanese or need to research large reports efficiently.

## 2. Problem Statement

Users face three major problems when researching long Japanese policy documents.

### 2.1 Keyword Search Limitations

Japanese text does not normally separate words with spaces. Keyword search can struggle with morphological variations, synonyms, technical terminology, and questions written in English when the relevant evidence appears in Japanese.

### 2.2 Time-Consuming Manual Research

Finding the answer to one question may require reading multiple sections or pages. Comparisons and summaries may require evidence from several parts of a report or multiple documents.

### 2.3 Unreliable General-Purpose Chatbot Answers

A general-purpose chatbot may not have access to the selected documents or their latest versions. It may generate plausible but unsupported claims, misinterpret numerical information, or provide citations that do not support its answer.

The problem is not simply generating an answer. It is retrieving the right evidence, explaining the answer, and allowing users to verify it against the original source.

## 3. Proposed Solution

Build a Retrieval-Augmented Generation (RAG) chatbot that allows users to ask questions in Japanese or English about a curated collection of Japanese policy and trade-related PDF documents.

The system will retrieve relevant source passages and use them to generate evidence-grounded answers with document and page references.

The initial workflow will be:

1. **Document ingestion:** Collect selected PDF documents and record their provenance and metadata.
2. **Text extraction:** Extract text while preserving page boundaries and identifying extraction failures.
3. **Chunking:** Split extracted text into meaningful passages while retaining document identifiers, page numbers, and available section metadata.
4. **Embedding generation:** Generate vector representations of the passages using a suitable embedding model.
5. **Vector indexing:** Use FAISS to index the passage vectors for similarity search. Store chunk text and metadata separately, linked through stable identifiers.
6. **Retrieval:** Retrieve relevant passages for Japanese and English queries.
7. **Answer generation:** Provide the retrieved evidence to a language model and instruct it to answer using that evidence.
8. **Citation presentation:** Display source document titles and page references that allow users to verify the answer.
9. **Abstention:** State when the available documents do not contain sufficient evidence rather than inventing an answer.

The initial implementation will prioritize reliable text retrieval, page-level traceability, and measurable evaluation. Advanced table extraction, OCR, hybrid retrieval, and reranking will be introduced when testing demonstrates a need.

## 4. Target Users

### 4.1 Policy Analysts and Researchers

Need to locate policy statements, statistics, economic trends, and supporting evidence across lengthy reports.

**Example:** Compare how two reports describe challenges facing a Japanese industry.

### 4.2 International Students and Professionals

Need to understand information in Japanese reports without manually reading every page in Japanese.

**Example:** Ask an English question and receive an answer grounded in a Japanese-language source.

### 4.3 Businesses and Market Researchers

Need to investigate Japanese industries, trade trends, and government initiatives.

**Example:** Identify a report's findings about an industry and locate the pages supporting those findings.

## 5. Example Questions

The evaluation dataset will cover both languages and multiple question types. Expected answers and source pages must be verified against the selected documents before evaluation.

### 5.1 Japanese Questions

1. **Factual lookup:** この白書の主な目的は何ですか。
2. **Numerical lookup:** この報告書によると、対象となる産業の市場規模はいくらですか。
3. **Cross-page summary:** この報告書の複数の章では、日本の経済成長についてどのように説明していますか。
4. **Comparison:** 2つの報告書では、対象となる産業の課題についてどのような違いがありますか。
5. **Unanswerable question:** この報告書に記載されていない2035年の正確な市場規模はいくらですか。

### 5.2 English Questions

1. **Factual lookup:** What is the main objective of this white paper?
2. **Numerical lookup:** According to the report, what is the market size of the selected industry?
3. **Cross-page summary:** How do different sections of the report describe Japan's economic growth?
4. **Comparison:** How do two reports differ in their descriptions of the challenges facing the selected industry?
5. **Unanswerable question:** What is the exact market size in 2035 if the selected documents do not provide that information?

These questions are templates. Before testing, replace generic references such as "this white paper" with specific questions tied to the actual corpus, and document the expected answer, required evidence, source pages, and whether abstention is appropriate.

## 6. Success Metrics

The following are provisional engineering targets, not measured results. They will be reviewed after establishing a baseline on a fixed evaluation dataset.

| Metric | Definition | Initial target |
|---|---|---:|
| Retrieval Recall@5 | Fraction of answerable questions for which at least one relevant evidence passage appears in the top five retrieved results | ≥ 85% |
| Required-evidence coverage | Fraction of multi-page questions for which all annotated required evidence passages or pages are retrieved within the chosen retrieval budget | ≥ 80% |
| Citation accuracy | Fraction of evaluated citations that point to the correct source and genuinely support the associated claim | ≥ 95% |
| Answer correctness | Fraction of evaluated answers judged correct against the source documents | ≥ 85% |
| Claim groundedness | Fraction of factual claims in generated answers supported by the cited or retrieved evidence | ≥ 90% |
| Out-of-corpus refusal rate | Fraction of unanswerable, out-of-corpus questions correctly refused or answered with an explicit insufficient-evidence response | ≥ 90% |
| In-corpus false-refusal rate | Fraction of answerable questions incorrectly refused despite sufficient evidence being available | ≤ 10% |
| Median response latency | Median time between submitting a question and receiving the answer | ≤ 10 seconds |

### 6.1 Evaluation Method

- Build a fixed dataset containing Japanese and English questions.
- Include factual lookups, numerical answers, cross-page summaries, comparisons, and unanswerable questions.
- Annotate the relevant evidence passages and required pages for each question.
- Evaluate simple retrieval questions separately from multi-page questions.
- Inspect citations against the original PDF pages.
- Measure retrieval quality separately from generated-answer quality.
- Record the number of test cases, model and embedding configurations, and evaluation procedure.
- Measure latency and model usage costs under a documented test setup.

Recall@5 alone is insufficient for a comparison question that requires evidence from multiple pages. Required-evidence coverage will help identify those failures.

The refusal metrics must be evaluated together: a system that refuses every question could score well on out-of-corpus refusal while being useless for answerable questions.

## 7. Non-Goals

The initial version will not attempt to:

1. Index every publication from METI, JETRO, or other Japanese institutions.
2. Guarantee accurate extraction from every scanned PDF, complex table, chart, or image.
3. Replace professional policy analysis or official government publications.
4. Answer arbitrary questions using unrestricted internet search.
5. Guarantee that a language model will never hallucinate.
6. Guarantee perfect Japanese-English translation or interpretation of technical terms.
7. Train a foundation language model from scratch.
8. Build a production-scale, multi-tenant enterprise platform.
9. Treat generated answers as verified facts without checking their supporting evidence.

The focus is a reproducible and measurable document research assistant rather than a universal chatbot.

## 8. Risks and Mitigations

### 8.1 PDF Parsing Quality

**Risk:** Text extraction may lose reading order, page boundaries, headings, or table structure. Scanned documents may contain no extractable text.

**Mitigation:** Inspect extracted text against original pages, retain page metadata, identify extraction failures, and evaluate OCR or specialized table extraction when necessary.

### 8.2 Japanese and Cross-Lingual Retrieval

**Risk:** Japanese terminology, morphological variations, domain-specific expressions, and English queries may reduce retrieval relevance.

**Mitigation:** Evaluate multilingual embeddings and Japanese-aware retrieval approaches using the same fixed evaluation dataset.

### 8.3 Numerical Accuracy

**Risk:** Tables may contain multiple units, fiscal years, percentages, and footnotes that are lost or misinterpreted.

**Mitigation:** Preserve table context where possible and verify numerical answers against the original source pages.

### 8.4 Hallucinations and Incorrect Citations

**Risk:** The language model may produce unsupported claims or cite pages that do not substantiate its answer.

**Mitigation:** Require evidence-grounded answers, validate citation metadata, evaluate claim groundedness, and test unanswerable questions.

### 8.5 Licensing and Provenance

**Risk:** Public accessibility does not automatically permit unrestricted redistribution of PDFs, extracted text, or derived datasets.

**Mitigation:** Record source URLs and applicable usage terms, check permissions before public redistribution, and provide attribution where required.

### 8.6 Latency and Cost

**Risk:** Embedding generation, reranking, and language-model inference may increase response time and operating costs.

**Mitigation:** Cache embeddings, avoid reprocessing unchanged documents, limit retrieved context, and measure the cost and latency of each configuration.

### 8.7 Outdated Information

**Risk:** An answer may accurately describe an older report but not reflect a more recent policy or statistic.

**Mitigation:** Preserve publication dates and document versions, display source metadata, and distinguish document-supported claims from claims about current conditions.

## 9. Motivation

I am building this project to explore how AI can make Japan's official policy and trade research more accessible to people who cannot easily read long Japanese documents. As I study Japanese and work toward an AI/ML engineering career, I want to solve a problem connected to both interests rather than build another generic chatbot.

I also want to understand the engineering behind a reliable RAG system, including document processing, cross-lingual retrieval, citation accuracy, and evaluation. The goal is to demonstrate not only that I can generate answers with an LLM, but also that I can measure whether the system retrieves the right evidence and knows when it cannot answer.

## 10. Initial Scope and Deliverables

The first version will include:

- A small, curated set of suitable Japanese PDF documents.
- Document provenance and metadata tracking.
- Text extraction and chunking with page references.
- Embedding generation and a persistent FAISS vector index.
- Separately stored chunk text and metadata.
- Japanese and English query handling.
- Evidence-grounded answer generation with page-level citations.
- An insufficient-evidence response.
- A fixed evaluation dataset and retrieval baseline.
- Documented evaluation results, limitations, and setup instructions.

OCR, advanced table extraction, hybrid retrieval, reranking, and a polished interface will be prioritized according to their measured impact.

## 11. Definition of Done

The initial project is complete when:

1. The selected documents can be ingested reproducibly.
2. Extracted passages retain correct document identifiers and page metadata.
3. Japanese and English questions can be submitted.
4. Answers include citations that can be checked against the original documents.
5. Unanswerable questions are evaluated without inventing unsupported facts.
6. Retrieval quality, answer correctness, citation accuracy, latency, and cost can be measured.
7. The evaluation procedure, results, and known limitations are documented.
8. Another developer can reproduce the setup using the project documentation.

The final objective is not merely to build a chatbot that generates fluent answers. It is to build a document research assistant whose answers are useful, evidence-grounded, traceable, and measurable.
