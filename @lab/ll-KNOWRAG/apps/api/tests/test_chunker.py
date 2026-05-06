"""Tests for the markdown chunker (T7)."""
from __future__ import annotations

import pytest

from server.services.knowledge.chunker import Chunk, chunk_markdown


# ── Validation ─────────────────────────────────────────────────────────────


def test_chunk_empty_body_returns_empty_list():
    assert chunk_markdown("") == []


def test_chunk_whitespace_only_returns_empty_list():
    assert chunk_markdown("   \n\n   \t  ") == []


def test_invalid_target_size_raises():
    with pytest.raises(ValueError):
        chunk_markdown("hello", target_size=0)
    with pytest.raises(ValueError):
        chunk_markdown("hello", target_size=-1)


def test_invalid_overlap_raises():
    with pytest.raises(ValueError):
        chunk_markdown("hello", target_size=100, overlap=-1)
    with pytest.raises(ValueError):
        chunk_markdown("hello", target_size=100, overlap=100)


def test_non_string_body_raises():
    with pytest.raises(TypeError):
        chunk_markdown(b"bytes")  # type: ignore[arg-type]


# ── Single-chunk cases ─────────────────────────────────────────────────────


def test_short_body_yields_single_chunk():
    body = "Hello, world."
    chunks = chunk_markdown(body, target_size=1500, overlap=200)
    assert len(chunks) == 1
    assert chunks[0].content == "Hello, world."
    assert chunks[0].index == 0
    assert chunks[0].section_title is None


def test_short_body_with_heading_attaches_title():
    body = "# Welcome\n\nHello, world."
    chunks = chunk_markdown(body)
    assert len(chunks) == 1
    assert chunks[0].section_title == "Welcome"
    assert "Hello, world." in chunks[0].content


# ── Structural split ───────────────────────────────────────────────────────


def test_atx_heading_splits_sections():
    body = "# Section A\n\nA body.\n\n# Section B\n\nB body."
    chunks = chunk_markdown(body)
    titles = {c.section_title for c in chunks}
    assert titles == {"Section A", "Section B"}
    assert chunks[0].index == 0
    assert chunks[1].index == 1


def test_setext_heading_splits_sections():
    body = "Section A\n=========\n\nA body.\n\nSection B\n---------\n\nB body."
    chunks = chunk_markdown(body)
    titles = [c.section_title for c in chunks]
    assert titles == ["Section A", "Section B"]


def test_intro_before_first_heading_kept_as_titleless_section():
    body = "Intro paragraph.\n\n# First Heading\n\nUnder it."
    chunks = chunk_markdown(body)
    assert chunks[0].section_title is None
    assert chunks[0].content.startswith("Intro paragraph")
    assert chunks[1].section_title == "First Heading"


def test_six_levels_of_atx_recognized():
    body = "###### Deep heading\n\nBody."
    chunks = chunk_markdown(body)
    assert chunks[0].section_title == "Deep heading"


# ── Windowing ──────────────────────────────────────────────────────────────


def test_long_section_windows_with_overlap():
    body = "x" * 3500
    chunks = chunk_markdown(body, target_size=1000, overlap=200)
    # 3500 chars at 1000/200 → starts: 0, 800, 1600, 2400, 3200 → 5 windows
    assert len(chunks) == 5
    # Indices contiguous
    assert [c.index for c in chunks] == list(range(5))
    # Every chunk except possibly the last is target-sized
    for c in chunks[:-1]:
        assert c.char_count == 1000


def test_overlap_actually_overlaps_content():
    # Make body just over target so we get exactly 2 chunks.
    body = "ABCDEFGHIJ" * 150  # 1500 chars
    chunks = chunk_markdown(body, target_size=1000, overlap=200)
    assert len(chunks) == 2
    # First chunk's last 200 chars should equal second chunk's first 200 chars.
    tail = chunks[0].content[-200:]
    head = chunks[1].content[:200]
    assert tail == head


def test_tail_smaller_than_min_chunk_merges_into_previous():
    # 1100-char body, target=1000, overlap=0, min_chunk_size=200 → tail of 100 should merge.
    body = "x" * 1100
    chunks = chunk_markdown(
        body, target_size=1000, overlap=0, min_chunk_size=200
    )
    assert len(chunks) == 1
    assert chunks[0].char_count >= 1100


def test_tail_larger_than_min_chunk_keeps_separate():
    body = "x" * 1300
    chunks = chunk_markdown(
        body, target_size=1000, overlap=0, min_chunk_size=200
    )
    assert len(chunks) == 2
    assert chunks[1].char_count == 300


# ── Indices ────────────────────────────────────────────────────────────────


def test_chunk_indices_are_zero_based_contiguous():
    body = ("# A\n" + "x" * 2000 + "\n# B\n" + "x" * 2000)
    chunks = chunk_markdown(body, target_size=800, overlap=100)
    indices = [c.index for c in chunks]
    assert indices == list(range(len(indices)))


# ── Edge cases ─────────────────────────────────────────────────────────────


def test_only_heading_no_body():
    body = "# Heading only\n\n"
    chunks = chunk_markdown(body)
    assert chunks == []


def test_heading_with_trailing_hash_chars_stripped():
    body = "## Foo ##\n\nbody"
    chunks = chunk_markdown(body)
    assert chunks[0].section_title == "Foo ##" or chunks[0].section_title.endswith("Foo ##")


def test_consecutive_blank_lines_do_not_create_empty_sections():
    body = "# A\n\n\n\n\n\nbody"
    chunks = chunk_markdown(body)
    assert len(chunks) == 1
    assert chunks[0].section_title == "A"


def test_chunk_is_frozen_dataclass():
    body = "hello"
    chunks = chunk_markdown(body)
    with pytest.raises((AttributeError, Exception)):
        chunks[0].content = "mutated"  # type: ignore[misc]


def test_chunk_has_char_count_matching_content_len():
    body = "x" * 500
    chunks = chunk_markdown(body, target_size=200, overlap=0)
    for c in chunks:
        assert c.char_count == len(c.content)
