#!/usr/bin/env python3
"""Download the METI source PDFs for the bilingual (EN/JA) RAG corpus.

Run from your repo root:
    python download_meti.py              # core set (8 files)
    python download_meti.py --extras     # core set plus the industry-facing extras
    python download_meti.py --dry-run    # print the plan, download nothing
    python download_meti.py --force      # re-download files that already exist

Standard library only. Optional: `pip install pypdf` to get page counts.

Writes:
    data/raw/*.pdf       (keep this folder git-ignored)
    data/manifest.csv    (commit this: source URL, access date, pages, licence,
                          and a third_party_notes column for you to fill in)
"""

import argparse
import csv
import datetime as dt
import hashlib
import shutil
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path

PAGE_BUDGET = 600  # total pages you want to keep CPU embedding quick

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

LICENCE_METI = (
    "METI Terms of Use (Public Data License 1.0); third-party material excluded"
)
LICENCE_MIC = (
    "Hosted on MIC site (soumu.go.jp): check its terms; "
    "English is a provisional translation"
)

try:  # helps on macOS Python installs that lack system certificates
    import certifi

    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CTX = None


FIELDS = [
    "filename",
    "doc",
    "corpus",
    "lang",
    "pair_id",
    "pair_quality",
    "source_url",
    "url_verified",
    "accessed",
    "pages",
    "size_kb",
    "sha256",
    "licence",
    "third_party_notes",
]


# --------------------------------------------------------------------------
# What to download
# --------------------------------------------------------------------------
def entry(
    doc, part, lang, url, pair_id="", group="core", licence=LICENCE_METI, hint=""
):
    return {
        "name": f"{doc}_{lang}_{part}.pdf",
        "doc": doc,
        "lang": lang,
        "url": url,
        "pair_id": pair_id,
        "group": group,
        "licence": licence,
        "hint": hint,
    }


def pair(
    doc,
    part,
    en_url,
    ja_url,
    group="core",
    licence=LICENCE_METI,
    hint_en="",
    hint_ja="",
):
    pid = f"{doc}:{part}"
    return [
        entry(doc, part, "en", en_url, pid, group, licence, hint_en),
        entry(doc, part, "ja", ja_url, pid, group, licence, hint_ja),
    ]


WP25_EN = "https://www.meti.go.jp/english/report/data/wp2025/pdf"
WP25_JA = "https://www.meti.go.jp/report/tsuhaku2025/pdf"
FULLTEXT_PAGE = "https://www.meti.go.jp/english/report/data/wp2025/wp2025.html"

FILES = []

# White Paper on International Economy and Trade 2025 (the anchor corpus)
D = "meti_trade_wp_2025"
FILES += pair(
    D,
    "exec-summary",
    "https://www.meti.go.jp/files/900011799.pdf",
    f"{WP25_JA}/2025_gaiyo.pdf",
)
FILES += pair(
    D,
    "overview-slides",
    "https://www.meti.go.jp/files/900011800.pdf",
    f"{WP25_JA}/2025_ppt.pdf",
)
FILES += pair(
    D,
    "p2-c1-s4_supply-chain-critical-minerals",
    f"{WP25_EN}/2-1-4.pdf",
    f"{WP25_JA}/2-1-4.pdf",
    group="later",
)
FILES += pair(
    D,
    "p2-c1-s5_industrial-policy",
    f"{WP25_EN}/2-1-5.pdf",
    f"{WP25_JA}/2-1-5.pdf",
    group="later",
)
FILES += pair(
    D,
    "p2-c2-s3_industry-case-studies",
    f"{WP25_EN}/2-2-3.pdf",
    f"{WP25_JA}/2-2-3.pdf",
    hint_en=(
        "This English URL follows METI's numbering but was not "
        f"confirmed. If it 404s, open {FULLTEXT_PAGE} and save "
        "Part II, Chapter 2, Section 3 under this file name."
    ),
    group="later",
)

FILES += pair(
    D,
    "p2-c3-s5_global-south-co-creation",
    f"{WP25_EN}/2-3-5.pdf",
    f"{WP25_JA}/2-3-5.pdf",
)

# White Paper 2026: English side is the summary only so far
FILES += pair(
    "meti_trade_wp_2026",
    "summary",
    "https://www.meti.go.jp/english/report/data/2026WTO/pdf/0630_001a.pdf",
    "https://www.meti.go.jp/report/tsuhaku2026/pdf/2026_gaiyo.pdf",
)

# 2025 Report on Compliance by Major Trading Partners (overview slides)
FILES += pair(
    "meti_compliance_2025",
    "overview-slides",
    "https://www.meti.go.jp/english/report/data/2025WTO/pdf/20250611_01en.pdf",
    "https://www.meti.go.jp/shingikai/sankoshin/tsusho_boeki/"
    "fukosei_boeki/report_2025/pdf/20250611_01.pdf",
    group="later",
)

# Industry-facing extras (only with --extras)
FILES += pair(
    "mic-meti_ai-guidelines_v1-2",
    "overview",
    "https://www.soumu.go.jp/main_content/001064309.pdf",
    "https://www.soumu.go.jp/main_content/001064299.pdf",
    group="extras",
    licence=LICENCE_MIC,
)
FILES.append(
    entry(
        "meti_monodzukuri_2026",
        "summary",
        "en",
        "https://www.meti.go.jp/files/000001760.pdf",
        group="extras",
        hint=(
            "The Japanese full report is an HTML index: "
            "https://www.meti.go.jp/report/whitepaper/mono/2026/index.html"
        ),
    )
)
FILES.append(
    entry(
        "meti_energy_wp_2025",
        "outline",
        "en",
        "https://www.enecho.meti.go.jp/en/category/whitepaper/pdf/2025_outline.pdf.pdf",
        group="extras",
        hint=(
            "If this 404s, open https://www.enecho.meti.go.jp/en/category/"
            "whitepaper and save the 2025 outline by hand."
        ),
    )
)
FILES.append(
    entry(
        "meti_compliance_2026",
        "overview-slides",
        "en",
        "https://www.meti.go.jp/english/report/data/2026WTO/pdf/20260612_01en.pdf",
        group="extras",
        hint="Japanese counterpart not confirmed yet.",
    )
)


# How each URL was checked. "index-page" = listed on METI's own index page
# (checked 2026-10-23). "fetched" = opened directly. Anything else is "no"
# until a download succeeds or you open the link yourself.
VERIFIED = {
    "https://www.meti.go.jp/files/900011799.pdf": "index-page",
    "https://www.meti.go.jp/files/900011800.pdf": "index-page",
    f"{WP25_JA}/2025_gaiyo.pdf": "index-page",
    f"{WP25_JA}/2025_ppt.pdf": "index-page",
    f"{WP25_JA}/2-1-4.pdf": "index-page",
    f"{WP25_JA}/2-1-5.pdf": "index-page",
    f"{WP25_JA}/2-2-3.pdf": "index-page",
    f"{WP25_JA}/2-3-5.pdf": "index-page",
    "https://www.meti.go.jp/english/report/data/2026WTO/pdf/0630_001a.pdf": "fetched",
}

# How closely the English and Japanese files match.
PAIR_QUALITY = {
    "meti_trade_wp_2025:exec-summary": "full",
    "meti_trade_wp_2025:overview-slides": "near",
    "meti_trade_wp_2025:p2-c3-s5_global-south-co-creation": "full",
    "meti_trade_wp_2026:summary": "partial",
}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def fetch(url, dest, retries=3, timeout=60):
    """Download url to dest. Returns (ok, message)."""
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept": "application/pdf,*/*"}
    )
    tmp = dest.with_suffix(dest.suffix + ".part")
    last = ""
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
                head = resp.read(1024)
                if b"%PDF-" not in head:
                    return False, "server did not return a PDF (HTML error page?)"
                with open(tmp, "wb") as out:
                    out.write(head)
                    shutil.copyfileobj(resp, out)
            tmp.replace(dest)
            return True, ""
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code < 500:  # 404 and friends: retrying will not help
                break
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last = str(getattr(e, "reason", e))
        time.sleep(2 * attempt)
    if tmp.exists():
        tmp.unlink()
    return False, last


def count_pages(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    try:
        return len(PdfReader(str(path)).pages)
    except Exception:
        return None


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_manifest(path):
    if not path.exists():
        return {}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return {row["filename"]: row for row in csv.DictReader(fh)}


def write_manifest(path, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        for name in sorted(rows):
            writer.writerow({k: rows[name].get(k, "") for k in FIELDS})


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--out", default="data/raw", help="download folder (default: data/raw)"
    )
    ap.add_argument(
        "--extras", action="store_true", help="also fetch the industry-facing extras"
    )
    ap.add_argument("--dry-run", action="store_true", help="print the plan and exit")
    ap.add_argument(
        "--force", action="store_true", help="re-download files that already exist"
    )
    ap.add_argument(
        "--budget",
        type=int,
        default=PAGE_BUDGET,
        help=f"page budget to check against (default {PAGE_BUDGET})",
    )
    ap.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="seconds to wait between downloads (default 1.0)",
    )
    args = ap.parse_args(argv)

    out = Path(args.out)
    manifest_path = out.parent / "manifest.csv"
    todo = [e for e in FILES if e["group"] == "core" or args.extras]

    if args.dry_run:
        for e in todo:
            print(f"{e['name']:<75} {e['url']}")
        print(f"\n{len(todo)} files -> {out}")
        return 0

    out.mkdir(parents=True, exist_ok=True)
    old = load_manifest(manifest_path)
    rows = dict(old)  # keep rows for files fetched in earlier runs
    failed = []
    today = dt.date.today().isoformat()

    for i, e in enumerate(todo, 1):
        dest = out / e["name"]
        tag = f"[{i}/{len(todo)}] {e['name']}"
        fetched = False
        if dest.exists() and not args.force:
            print(f"{tag}: already there, skipping")
            accessed = (
                old.get(e["name"], {}).get("accessed")
                or dt.date.fromtimestamp(dest.stat().st_mtime).isoformat()
            )
        else:
            ok, msg = fetch(e["url"], dest)
            if not ok:
                print(f"{tag}: FAILED ({msg})")
                failed.append((e, msg))
                continue
            print(f"{tag}: ok")
            fetched = True
            accessed = today
            time.sleep(args.delay)  # be polite to the server

        pages = count_pages(dest)
        prev = old.get(e["name"], {})
        rows[e["name"]] = {
            "filename": e["name"],
            "doc": e["doc"],
            "lang": e["lang"],
            "pair_id": e["pair_id"],
            "source_url": e["url"],
            "accessed": accessed,
            "pages": "" if pages is None else pages,
            "size_kb": round(dest.stat().st_size / 1024),
            "licence": e["licence"],
            "third_party_notes": prev.get("third_party_notes", ""),
            "corpus": prev.get("corpus") or "trade",
            "pair_quality": PAIR_QUALITY.get(e["pair_id"])
            or prev.get("pair_quality", ""),
            "url_verified": (
                "downloaded"
                if fetched
                else (VERIFIED.get(e["url"]) or prev.get("url_verified") or "no")
            ),
            "sha256": sha256(dest),
        }

    write_manifest(manifest_path, rows)

    # Summary
    print()
    total, unknown = 0, 0
    for e in todo:
        r = rows.get(e["name"])
        if not r or not (out / e["name"]).exists():
            continue
        if r["pages"] == "":
            unknown += 1
        else:
            total += int(r["pages"])
        shown = r["pages"] if r["pages"] != "" else "?"
        print(f"  {e['name']:<72} {shown:>5} pages  {r['size_kb']:>6} KB")
    if unknown:
        print("\nPage counts need pypdf:  pip install pypdf")
    verdict = "OVER budget" if total > args.budget else "within budget"
    print(f"\nPages counted: {total} (budget {args.budget}) -> {verdict}")
    print(f"Manifest: {manifest_path}  (fill in third_party_notes for each file)")

    if failed:
        print(f"\n{len(failed)} file(s) failed:")
        for e, msg in failed:
            print(f"  - {e['name']}: {msg}\n    {e['url']}")
            if e["hint"]:
                print(f"    hint: {e['hint']}")
        print(
            "\nSave any missing file by hand into the same folder under the "
            "same name, then re-run to add it to the manifest."
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
