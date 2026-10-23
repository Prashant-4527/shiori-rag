# Apply the Day 2 fixes (PowerShell, from the repo root)

Do the steps in order. Do NOT commit anything in rewrite-history/. Those files contain your personal email address.

## 0. Back up first
    Copy-Item -Recurse D:\Career\Projects\shiori-rag D:\Career\Projects\shiori-rag-backup

## 1. Copy the files in
Copy from this folder into the repo, overwriting: scripts\download_meti.py, data\manifest.csv, docs\DATA_CARD.md, README.md, pyproject.toml.
Copy experiments\v0_notes_template.md into experiments\.
Open docs\decisions.md. Paste the contents of docs\decisions_append.md at the end. In ADR-001 change the Status line to:
    - **Status:** Accepted; partially superseded by ADR-006 (JETRO excluded from the public corpus)
Then fix ADR-001's title and the JETRO mentions in docs\PROBLEM.md so they match ADR-006.

## 2. Remove the duplicate manifest script
    git rm scripts/build_manifest.py

## 3. Check your files and rebuild the manifest from YOUR copies
    dir data\raw
You need 8 files, all named meti_trade_wp_*. Then:
    uv run python scripts/download_meti.py
    uv run pytest
    uv run ruff check .
Open data\manifest.csv. Open the URLs of the two rows marked "no" (EN 2-3-5, JA 2026 summary) in a browser; if they show the right PDF, change "no" to "browser". Re-read the third_party_notes column.

## 4. Commit (three commits)
    git add scripts/download_meti.py data/manifest.csv
    git commit -m "feat: METI downloader with manifest, checksums and URL verification status"
    git add docs/DATA_CARD.md docs/decisions.md docs/PROBLEM.md
    git commit -m "docs: add data card and ADR-002 to ADR-008, scope corpus to METI"
    git add README.md pyproject.toml
    git commit -m "docs: add README and project metadata"

## 5. Clean the history (removes the Gmail address and the old author names)
Your public history still contains your personal email (old commits that came back when you merged) and the author name Rintaro in pyproject.toml.
Put mailmap.txt and replace.txt in the PARENT folder (D:\Career\Projects), not in the repo. Then:
    git status                      # must say: nothing to commit
    pip install git-filter-repo
    git filter-repo --mailmap ..\mailmap.txt --replace-text ..\replace.txt --force
    git remote add origin https://github.com/Prashant-4527/shiori-rag.git
    git push --force origin main
    git log --format="%an <%ae> | %s"
Every line should show the noreply address. Delete mailmap.txt and replace.txt afterwards.
GitHub may keep old commits reachable by their SHA for a while, so treat the old email as already public.
Also turn on "Keep my email addresses private" and "Block command line pushes that expose my email" in GitHub, Settings, Emails.

## 6. GitHub About box
Description: Bilingual (JA/EN) RAG over METI trade white papers, with page-level citations
Topics: rag, nlp, japanese, retrieval-augmented-generation, sentence-transformers, faiss

## 7. Run v0 (this is Day 2's core exercise)
    ollama list
    uv run python experiments/v0_naive.py data/raw/meti_trade_wp_2025_ja_exec-summary.pdf
Then the slide deck:
    uv run python experiments/v0_naive.py data/raw/meti_trade_wp_2025_ja_overview-slides.pdf
Fill experiments\v0_notes_template.md, save it as experiments\v0_notes.md, and commit:
    git add experiments pyproject.toml uv.lock
    git commit -m "experiment: naive RAG v0 run and failure notes"
    git push
