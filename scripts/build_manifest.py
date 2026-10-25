import csv
import hashlib

from pypdf import PdfReader

from shiori_rag.config import DATA_DIR, RAW_DIR

OUT = DATA_DIR / "manifest.csv"
FIELDS = [
    "doc_id",
    "filename",
    "pages",
    "sha256",
    "language",
    "publisher",
    "title",
    "source_url",
    "published",
    "retrieved",
    "licence",
    "third_party_notes",
]


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)

    return h.hexdigest()


def load_existing():
    if not OUT.exists():
        return {}

    with OUT.open(encoding="utf-8-sig", newline="") as f:
        return {row["filename"]: row for row in csv.DictReader(f)}


def main():
    existing = load_existing()
    rows = []
    for pdf in sorted(RAW_DIR.glob("*.pdf")):
        row = existing.get(pdf.name, {k: "" for k in FIELDS})
        row.update(
            doc_id=pdf.stem,
            filename=pdf.name,
            pages=len(PdfReader(pdf).pages),
            sha256=sha256(pdf),
        )
        rows.append(row)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(rows)

    print(f"{len(rows)} documents written to {OUT}")


if __name__ == "__main__":
    main()
