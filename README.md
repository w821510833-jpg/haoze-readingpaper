# Haoze Reading Paper

A Codex skill for reading and understanding local academic paper PDFs.

## What It Does

- Stage 1: create a beginner-friendly, source-linked paper overview.
- Stage 2: analyze every figure and table for close reading.
- Stage 3: support paper-grounded Q&A.
- Stage 4: generate final reading notes for Obsidian or Zotero.

This skill is intentionally focused on reading one paper at a time. It does not search for papers, create daily digests, or act as a citation-only tool.

## Structure

- `SKILL.md` - main Codex skill instructions
- `agents/openai.yaml` - UI metadata
- `references/template.css` - base HTML style
- `scripts/extract_pdf_text.py` - local PDF text extraction helper
- `scripts/extract_visual_index.py` - section, figure, and table index helper
