#!/usr/bin/env python3
"""Build a lightweight section, figure, and table index from Haoze Reading Paper PDF text JSON."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SECTION_RE = re.compile(r"\b([1-9](?:\.\d+){0,3})\.\s+([A-Z][^\n\.]{2,100})")
FIGURE_RE = re.compile(r"\b(?:Fig\.|Figure)\s+(\d+)\.?\s+(.{20,700}?)(?=(?:\b(?:Fig\.|Figure)\s+\d+\.?\s+)|(?:\bTable\s+\d+)|(?:\n?\s*\d+(?:\.\d+)*\.\s+[A-Z])|$)", re.S)
TABLE_RE = re.compile(r"\bTable\s+(\d+)\s+(.{20,700}?)(?=(?:\bTable\s+\d+)|(?:\b(?:Fig\.|Figure)\s+\d+\.?\s+)|(?:\n?\s*\d+(?:\.\d+)*\.\s+[A-Z])|$)", re.S)
REFERENCE_STARTS = (
    "shows", "show", "reports", "report", "depicts", "depict", "presents",
    "present", "indicates", "indicate", "illustrates", "illustrate", "is ",
    "are ", ").", "):",
)
MAJOR_SECTION_STARTS = {
    "1": ("introduction",),
    "2": ("materials", "methods"),
    "3": ("results",),
    "4": ("discussion",),
    "5": ("conclusion", "conclusions"),
}


def clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "")
    return text.strip(" .\n\t")


def make_pdf_link(pdf: str | None, page: int) -> str:
    if not pdf:
        return f"#page={page}"
    return f"{Path(pdf).name}#page={page}"


def looks_like_reference(caption: str) -> bool:
    lowered = caption.lower().lstrip()
    return lowered.startswith(REFERENCE_STARTS)


def looks_like_section(number: str, title: str, prefix: str) -> bool:
    lowered_prefix = prefix.lower()
    if "fig" in lowered_prefix or "table" in lowered_prefix:
        return False

    title = clean(title)
    words = title.split()
    if not words or len(words) > 12:
        return False

    first = number.split(".")[0]
    lowered_title = title.lower()
    if "." not in number:
        allowed = MAJOR_SECTION_STARTS.get(first, ())
        return any(lowered_title.startswith(item) for item in allowed)

    if words[0].lower() in {"the", "this", "these", "those", "a", "an", "in", "for", "of"}:
        return False

    return first in MAJOR_SECTION_STARTS


def build_index(extract: dict, pdf: str | None) -> dict:
    sections = []
    visuals = []
    current_section = ""

    for page in extract.get("pages", []):
        page_no = int(page.get("page", 0))
        text = page.get("text", "")

        for section_match in SECTION_RE.finditer(text):
            prefix = text[max(0, section_match.start() - 12):section_match.start()].lower()
            number = section_match.group(1)
            title = section_match.group(2)
            if not looks_like_section(number, title, prefix):
                continue
            current_section = f"{number}. {clean(title)}"
            sections.append({
                "section": current_section,
                "page": page_no,
                "pdf_link": make_pdf_link(pdf, page_no),
            })

        for kind, regex in (("figure", FIGURE_RE), ("table", TABLE_RE)):
            for match in regex.finditer(text):
                number = match.group(1)
                caption = clean(match.group(2))
                if not caption or looks_like_reference(caption):
                    continue
                visuals.append({
                    "kind": kind,
                    "number": number,
                    "label": f"{'Fig.' if kind == 'figure' else 'Table'} {number}",
                    "caption": caption[:900],
                    "page": page_no,
                    "section": current_section,
                    "pdf_link": make_pdf_link(pdf, page_no),
                })

    return {
        "source_pdf": pdf or extract.get("source_pdf", ""),
        "page_count": extract.get("page_count"),
        "sections": sections,
        "visuals": visuals,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a source-linked visual index from Haoze Reading Paper JSON.")
    parser.add_argument("extract_json", help="JSON produced by extract_pdf_text.py")
    parser.add_argument("--pdf", help="Original PDF path for page links")
    parser.add_argument("--out", help="Optional JSON output path")
    args = parser.parse_args()

    data = json.loads(Path(args.extract_json).read_text(encoding="utf-8"))
    index = build_index(data, args.pdf)
    payload = json.dumps(index, ensure_ascii=False, indent=2)

    if args.out:
        out = Path(args.out).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
        print(str(out))
    else:
        print(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
