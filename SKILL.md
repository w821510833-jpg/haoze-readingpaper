---
name: haoze-readingpaper
description: Academic paper reading workflow for Codex. Use when the user asks to read, understand, explain, annotate, or deeply analyze a local research paper PDF; create beginner-friendly paper overviews; analyze figures and tables; support paper-focused Q&A; or generate final reading notes for Obsidian/Zotero after the reading process.
---

# Haoze Reading Paper

Use this skill only for reading and understanding academic papers. It is not a literature-search, daily-digest, or citation-only skill.

This workflow focuses on one paper at a time: extract the PDF, create a source-linked overview, optionally analyze figures and tables, support follow-up Q&A, and finally produce a durable reading note.

## Stage Triggers

Default to **Stage 1 only**. Do not automatically proceed to figure/table deep reading, Q&A synthesis, or final notes unless the user explicitly asks for that stage.

| Stage | User intent | Output |
| --- | --- | --- |
| Stage 1: triage overview | overview, quick read, is this worth reading, stage 1, initial paper overview | Beginner-friendly HTML or chat report with source links |
| Stage 2: figure/table deep dive | figure analysis, table analysis, deep read, stage 2, analyze every figure/table | Detailed figure/table HTML or Markdown |
| Stage 3: Q&A | I have questions, Q&A, explain more, continue explaining | Conversational answers grounded in the paper and previous artifacts |
| Stage 4: final note | final note, Obsidian, Zotero, stage 4, reading note | Obsidian/Zotero-friendly Markdown, optionally paired with HTML |

If the user only says "analyze/read this paper" without specifying a stage, run Stage 1 and stop. End by briefly telling the user what Stage 2 would add, but do not create it yet.

## Defaults

Use these defaults unless the user or project context says otherwise:

```yaml
output_dir: "./papers"
annotation_lang: zh
```

Project-level overrides may appear in `AGENTS.md`, local notes, or the user request:

```yaml
readingpaper_output_dir: 30_Research
readingpaper_annotation_lang: en
```

## Core Workflow

1. Resolve the requested reading stage.
2. Resolve output directory from the user request, project context, or `output_dir`.
3. For local PDFs, extract text with `scripts/extract_pdf_text.py`.
4. For source links and figure/table analysis, build a visual/section index with `scripts/extract_visual_index.py`.
5. If generating HTML, embed `references/template.css` in a `<style>` block and create a self-contained file.
6. Report saved file paths and a concise reading summary.

On Windows, avoid piping non-ASCII HTML or Markdown source through PowerShell stdin; write from a UTF-8 script file or a Unicode-safe runtime so Chinese text is not replaced with `?`.

## Stage 1: Triage Overview

Use Stage 1 to answer: "What is this paper about, and is it worth reading deeply?"

For requests like "analyze this PDF", "read this paper", or "overview this paper":

1. Run:

```powershell
python scripts/extract_pdf_text.py "paper.pdf" --out "readingpaper-extract.json"
```

Use the bundled Codex Python path if the system `python` command is unavailable.

2. Extract title, authors, year, venue, DOI, abstract, conclusion, and main body structure when possible.
3. Build a beginner-friendly overview in chat or HTML.

For beginner-friendly reports, include:

- Paper identity: title, authors, venue/year, DOI when available.
- Plain-language takeaway: explain the paper in 3-5 sentences without jargon.
- Background primer: define domain terms, acronyms, and why the problem matters.
- Research problem: what gap or bottleneck the paper targets.
- Method: what the authors actually did.
- Core findings: 3-6 high-signal points.
- Reading map: which sections to read first and what to watch for.
- Worth-reading judgment: who should continue to Stage 2 and why.

For overview HTML, include source links for key claims. Link to local PDF pages with relative links such as `../paper.pdf#page=7` when possible.

## Stage 2: Figure And Table Deep Dive

Use Stage 2 only when the user asks for close reading, figure analysis, table analysis, intensive reading, or a deep read.

First build the visual index:

```powershell
python scripts/extract_visual_index.py "readingpaper-extract.json" --pdf "paper.pdf" --out "readingpaper-visual-index.json"
```

Then produce a separate figure/table HTML or Markdown section. For every figure and table:

- Identify where it appears: page number, caption, section, and PDF page link.
- Explain its role in the paper: motivation, method evidence, result evidence, comparison, ablation, validation, limitation, or summary.
- Explain how to read it for beginners: axes, variables, units, color/marker meaning, rows/columns, subpanels, and what to compare first.
- State the local takeaway: what this visual proves or supports.
- State the global takeaway: how it advances the paper's main argument.
- Add caveats: missing controls, hard-to-see assumptions, statistical uncertainty, or overclaiming.
- Add follow-up questions the user may ask in Stage 3.

Do not skip tables. Tables often contain dataset splits, model scores, hyperparameters, or feature definitions that are essential for judging the paper.

Treat the visual index as a draft map. PDF text extraction can confuse figure references with figure captions, especially in Elsevier-style PDFs. Before producing the final deep dive, deduplicate labels, remove in-text references such as "Fig. 2 shows...", and verify each figure/table against the PDF page.

## Stage 3: Q&A

Use Stage 3 when the user asks follow-up questions after overview or figure/table reading.

- Answer from the paper first, then add explanation.
- If the question depends on a specific figure, table, formula, or paragraph, verify the source location before answering.
- Explain jargon in plain language when the user appears new to the field.
- Keep track of clarified points that should later appear in the final note.
- If the paper does not answer the question, say so and distinguish inference from source-supported claims.

## Stage 4: Final Reading Note

Treat final notes as the last stage, not the first output. Build them after overview, figure/table deep dive, and Q&A.

For Obsidian/Zotero-friendly Markdown:

- Use YAML frontmatter with `title`, `authors`, `year`, `venue`, `doi`, `tags`, and `zotero_key` when known.
- Include short sections: `One-sentence takeaway`, `Why I read this`, `Background`, `Method`, `Figures and tables`, `Key claims`, `Limitations`, `My questions`, `Connections`, `Citation`.
- Include citation metadata as supporting information, but do not treat citation generation as a separate task.
- Use wiki links only when the user's vault style is known; otherwise use plain Markdown links.
- Link source evidence to local PDF pages or DOI links wherever possible.
- Keep the note readable as a future review artifact, not just a transcript of the analysis.

## HTML Guidance

For generated reading HTML:

- Top navbar with paper title, context label, and stage label.
- Beginner-friendly sections before technical details when the user may be new to the field.
- Source links for key claims and summaries.
- Figure/table cards for Stage 2.
- Bottom overview with the paper's main claim, strongest evidence, weakest point, and next questions.
- Use `references/template.css` as the base style.

Do not translate original paper excerpts unless the user asks for translation. Use `annotation_lang` for summaries and explanations.

## Error Handling

- If the PDF is unreadable, say which path failed and suggest checking whether it is scanned or permission-protected.
- If extraction returns very little text, try OCR only if tools are available and the user wants a deeper pass.
- If metadata is uncertain, mark it as best effort instead of inventing details.
- If figure/table extraction is noisy, treat it as a draft index and manually verify against the PDF before generating Stage 2 output.
