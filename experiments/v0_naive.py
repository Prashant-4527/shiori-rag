"""Naive RAG v0. Throwaway on purpose: its job is to fail in instructive ways."""

import os
import sys
from pathlib import Path

import numpy as np
import ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")
TOP_K = 5

if len(sys.argv) < 2:
    print("Usage: python experiments/v0_naive.py <path_to_pdf>")
    sys.exit(1)

pdf_path = Path(sys.argv[1])

if not pdf_path.is_file():
    print(f"Error: PDF file not found: {pdf_path}")
    sys.exit(1)


reader = PdfReader(pdf_path)
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

chunks = []


for page_no, page in enumerate(reader.pages, start=1):
    for piece in splitter.split_text(page.extract_text() or ""):
        chunks.append((page_no, piece))
print(f"{len(reader.pages)} pages -> {len(chunks)} chunks")


model = SentenceTransformer("BAAI/bge-m3")
vectors = model.encode(
    [text for _, text in chunks],
    normalize_embeddings=True,
    batch_size=16,
    show_progress_bar=True,
)


while True:
    question = input("\nQuestionn (blank to quit): ").strip()
    if not question:
        break

    q_vec = model.encode([question], normalize_embeddings=True)[0]
    scores = vectors @ q_vec
    hits = [chunks[i] for i in np.argsort(-scores)[:TOP_K]]
    for rank, (page_no, text) in enumerate(hits, start=1):
        print(
            f"\n#{rank} page={page_no} score={scores[np.argsort(-scores)[rank - 1]]:.3f}\n{text}"
        )
    context = "\n\n".join(f"[p.{p}] {t}" for p, t in hits)
    prompt = (
        "Answer using only the context. If the context does not contain the answer, "
        f"say so.\n\nContext:\n{context}\n\nQuestion: {question}"
    )
    reply = ollama.chat(
        model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}]
    )
    print("\nANSWER:", reply["message"]["content"])
