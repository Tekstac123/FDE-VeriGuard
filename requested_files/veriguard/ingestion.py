"""Week 1 · Task 1 — Document processing: page-aware, clause-level chunks that carry the manifest's metadata.

Reads DCB's corpus in both formats (PDF and Markdown), splits each document at its numbered sections, and
attaches the metadata every later control depends on: version and status (superseded traps), classification and
access_roles (security trimming), section and page (citations an auditor can follow).

Find your work with:  grep -n "TODO" veriguard/ingestion.py
Check it with:        python check_week1.py --task 1
"""
from __future__ import annotations

from pathlib import Path

from .common import (  # noqa: F401 — helpers you will need
    DOCS, PAGE_NOISE, SECTION_HEADING, doc_type_of, document_lines, load_manifest, split_words)

# ─── WEEK 1 · L0 + M1 Grounded Financial Intelligence — you implement the stubbed functions in this file in Week 1 ───


def extract_sections(path: Path, title: str) -> list[dict]:
    """The numbered sections of one document: [{"section", "heading", "page", "text"}] in document order."""
    # TODO [W1-T1.1] extract_sections — split ONE document into its numbered sections.
    #   What to do:
    #   1. Loop over document_lines(path) (common.py). It yields (page, line, is_heading_style) for PDF and Markdown:
    #      PDF → page 1, 2, … and is_heading_style False · MD → page None, is_heading_style True for '## ' headings.
    #   2. Skip page furniture: a line equal to `title`, or any line that matches PAGE_NOISE
    #      ("Page 2", "SYNTHETIC TRAINING DATA - FICTIONAL ENTITY", "Document ID: …", the bank's header, "# …").
    #   3. A NEW section starts on a line that matches SECTION_HEADING (e.g. "4. Enhanced Due Diligence for PEPs")
    #      AND (is_heading_style is True OR the file is a .pdf). Use the regex groups "section" and "heading"
    #      (strip the heading). Record the page of that line as the section's page.
    #   4. Every other line belongs to the current section; lines before the first heading are ignored.
    #   5. Return one dict per section, in order: {"section": "4", "heading": "Enhanced Due Diligence for PEPs",
    #      "page": 2 (None for Markdown), "text": <the section's lines joined with single spaces>}.
    #   Expected: DCB-POL-KYC_v4_0.pdf → sections "1".."7"; §4 starts on page 2 and its text contains "12 months".
    #             DCB-SOP-TMI_v3_0.md → 5 sections, page None · DCB-HB-TYP_v2_0.md → 6 sections, no front matter.
    raise NotImplementedError("extract_sections is not yet implemented")


def build_chunks(meta: dict, sections: list[dict], max_words: int = 120, overlap: int = 20) -> list[dict]:
    """Chunk dicts for one document version: one per section (long sections windowed), manifest metadata on each.

    Keys: id ("<doc_id>:<version>:<section>:<chunk_no>"), doc_id, title, doc_type, version, status (lower-case),
    effective_date, superseded_by, classification, access_roles (list), source, section, heading, page, chunk_no,
    text ("<heading>. <window>").
    """
    # TODO [W1-T1.2] build_chunks — turn the sections of ONE manifest row into searchable chunks.
    #   What to do:
    #   1. `meta` is one row of corpus_manifest.csv — the source of truth. Copy onto EVERY chunk:
    #      doc_id, title, version, effective_date, classification, source (= meta["file"]),
    #      status = meta["status"].lower()  ("current" / "superseded"),
    #      superseded_by = meta["superseded_by"] or None  (empty string → None),
    #      access_roles = meta["access_roles"] split on ";" into a list (strip blanks),
    #      doc_type = doc_type_of(meta["doc_id"])  ("DCB-POL-KYC" → "policy").
    #   2. For each section, window its text with split_words(text, max_words, overlap); a section with no words
    #      still gives one (empty) window. chunk_no counts the windows of that section from 0.
    #   3. Each chunk also gets: section, heading, page (from the section), chunk_no,
    #      id = f"{doc_id}:{version}:{section}:{chunk_no}"   e.g. "DCB-POL-KYC:4.0:4:0",
    #      text = f"{heading}. {window}" (stripped)            e.g. "Enhanced Due Diligence for PEPs. Onboarding …".
    #   Expected: build_corpus() returns 92 chunks from 22 document versions; DCB-POL-KYC v3.2 chunks have
    #             status "superseded" and superseded_by "4.0"; DCB-IA-2026-06 chunks are Board-Restricted, ["Auditor"].
    raise NotImplementedError("build_chunks is not yet implemented")


# ----------------------------------------------------------------------------- provided
def build_corpus() -> list[dict]:
    """PROVIDED — every chunk of every document version listed in the manifest (superseded versions included)."""
    chunks: list[dict] = []
    for meta in load_manifest():
        chunks.extend(build_chunks(meta, extract_sections(DOCS / meta["file"], meta["title"])))
    return chunks
