#!/usr/bin/env python3
"""Extract text and lightweight metadata from a PDF for Haoze Reading Paper."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader


def compact_ws(text: str) -> str:
    return re.sub(r"[ \t\r\f\v]+", " ", text or "").strip()


def word_window(text: str, n: int, tail: bool = False) -> str:
    words = re.findall(r"\S+", text or "")
    if not words:
        return ""
    selected = words[-n:] if tail else words[:n]
    return " ".join(selected)


def metadata_value(metadata, key: str) -> str:
    if not metadata:
        return ""
    value = metadata.get(key) or metadata.get(key.lstrip("/"))
    return compact_ws(str(value)) if value else ""


def extract(pdf_path: Path, max_pages: int | None) -> dict:
    reader = PdfReader(str(pdf_path))
    page_count = len(reader.pages)
    limit = min(page_count, max_pages) if max_pages else page_count

    pages = []
    for idx in range(limit):
        try:
            text = reader.pages[idx].extract_text() or ""
        except Exception as exc:  # keep partial extraction useful
            text = f"[PAGE EXTRACTION ERROR: {exc}]"
        pages.append({"page": idx + 1, "text": compact_ws(text)})

    full_text = "\n\n".join(page["text"] for page in pages if page["text"])
    metadata = reader.metadata

    return {
        "source_pdf": str(pdf_path),
        "page_count": page_count,
        "extracted_pages": limit,
        "metadata": {
            "title": metadata_value(metadata, "/Title"),
            "author": metadata_value(metadata, "/Author"),
            "subject": metadata_value(metadata, "/Subject"),
            "creator": metadata_value(metadata, "/Creator"),
            "producer": metadata_value(metadata, "/Producer"),
        },
        "first_300_words": word_window(full_text, 300),
        "last_300_words": word_window(full_text, 300, tail=True),
        "pages": pages,
        "full_text": full_text,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract PDF text for Haoze Reading Paper.")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("--out", help="Optional JSON output path")
    parser.add_argument("--max-pages", type=int, default=None, help="Limit extraction to the first N pages")
    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        return 2

    data = extract(pdf_path, args.max_pages)
    payload = json.dumps(data, ensure_ascii=False, indent=2)

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload, encoding="utf-8")
        print(str(out_path))
    else:
        print(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
