"""Markdown chunker (Phase 8).

Two-stage strategy carried over from Phase 7 (BLUEPRINT §10):

1. **Structural split** on markdown headings (ATX ``#``-style and Setext
   ``===``/``---`` underlines). Each heading starts a new section that is
   chunked independently.
2. **Fallback windowing** within a section: target 1500 chars per chunk
   with 200 char overlap.

The chunker emits plain :class:`Chunk` dataclasses — no DB-tied fields.
Storage layer (Qdrant) decorates these with ``artifact_path`` /
``commit_sha`` / frontmatter on upsert.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

ATX_HEADING_RE = re.compile(r"^#{1,6}\s+(\S.*)$")
SETEXT_UNDERLINE_RE = re.compile(r"^[=-]{3,}\s*$")


@dataclass(frozen=True)
class Chunk:
    """A unit of text ready for embedding + indexing."""

    index: int
    content: str
    char_count: int
    section_title: str | None = None


def chunk_markdown(
    body: str,
    *,
    target_size: int = 1500,
    overlap: int = 200,
    min_chunk_size: int = 100,
) -> list[Chunk]:
    """Two-stage chunker. Returns chunks in document order.

    Args:
        body: the markdown body (without frontmatter).
        target_size: target chars per chunk.
        overlap: char overlap between adjacent chunks within a section.
        min_chunk_size: tail chunks smaller than this are merged into the
            previous chunk to avoid noise.
    """
    if not isinstance(body, str):
        raise TypeError("body must be a string")
    if target_size <= 0:
        raise ValueError("target_size must be > 0")
    if overlap < 0 or overlap >= target_size:
        raise ValueError("overlap must be >= 0 and < target_size")
    if min_chunk_size < 0:
        raise ValueError("min_chunk_size must be >= 0")

    if not body.strip():
        return []

    sections = _split_sections(body)
    chunks: list[Chunk] = []
    idx = 0
    for title, content in sections:
        content = content.strip()
        if not content:
            continue
        start = 0
        section_chunks: list[Chunk] = []
        while start < len(content):
            end = start + target_size
            text = content[start:end].strip()
            if not text:
                break
            section_chunks.append(
                Chunk(
                    index=idx,
                    content=text,
                    char_count=len(text),
                    section_title=title,
                )
            )
            idx += 1
            if end >= len(content):
                break
            start = end - overlap

        # Merge undersized tail chunk into its predecessor.
        if (
            len(section_chunks) >= 2
            and section_chunks[-1].char_count < min_chunk_size
        ):
            tail = section_chunks.pop()
            prev = section_chunks[-1]
            merged = (prev.content + "\n\n" + tail.content).strip()
            section_chunks[-1] = Chunk(
                index=prev.index,
                content=merged,
                char_count=len(merged),
                section_title=prev.section_title,
            )
            idx -= 1  # we removed one, keep indices contiguous

        chunks.extend(section_chunks)

    # Re-number contiguously (defensive — merging may have left gaps).
    return [
        Chunk(
            index=i,
            content=c.content,
            char_count=c.char_count,
            section_title=c.section_title,
        )
        for i, c in enumerate(chunks)
    ]


def _split_sections(body: str) -> list[tuple[str | None, str]]:
    """Split body into (section_title, content) pairs by markdown headings."""
    lines = body.splitlines()
    sections: list[tuple[str | None, str]] = []
    current_title: str | None = None
    current_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        atx = ATX_HEADING_RE.match(line)
        if atx:
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = atx.group(1).strip()
            current_lines = []
            i += 1
            continue
        # Setext heading: a non-empty line followed by ===/---.
        if (
            line.strip()
            and i + 1 < len(lines)
            and SETEXT_UNDERLINE_RE.match(lines[i + 1])
        ):
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = line.strip()
            current_lines = []
            i += 2
            continue
        current_lines.append(line)
        i += 1
    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))
    if not sections:
        return [(None, body)]
    return sections


__all__ = ["Chunk", "chunk_markdown"]
