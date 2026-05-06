"""Tests for frontmatter parser (T6)."""
from __future__ import annotations

import pytest

from server.services.knowledge.frontmatter import (
    Frontmatter,
    FrontmatterError,
    parse,
    serialize,
)


# ── Happy path ─────────────────────────────────────────────────────────────

def test_parse_full_frontmatter():
    content = """---
id: a3f2-9b1c
tags: [agents, mcp, claude]
status: published
version: 1.2.0
owner: w7-mgfcode
visibility: public
created_at: 2026-04-15
updated_at: 2026-05-06
---

# Title

Body."""
    meta, body = parse(content)
    assert meta.id == "a3f2-9b1c"
    assert meta.tags == ["agents", "mcp", "claude"]
    assert meta.status == "published"
    assert meta.version == "1.2.0"
    assert meta.owner == "w7-mgfcode"
    assert meta.visibility == "public"
    assert str(meta.created_at) == "2026-04-15"
    assert body.startswith("# Title")


def test_parse_minimal_required_fields():
    content = "---\nid: x\nowner: y\n---\nbody"
    meta, body = parse(content)
    assert meta.id == "x"
    assert meta.owner == "y"
    assert meta.status == "draft"  # default
    assert meta.visibility == "private"  # default
    assert meta.tags == []
    assert meta.version == "0.1.0"
    assert body == "body"


def test_parse_empty_frontmatter_block_rejected():
    """An empty frontmatter is rejected — id and owner are required."""
    content = "---\n---\nbody"
    with pytest.raises(FrontmatterError, match="schema|missing"):
        parse(content)


def test_parse_tolerates_bom():
    content = "﻿---\nid: x\nowner: y\n---\nbody"
    meta, body = parse(content)
    assert meta.id == "x"
    assert body == "body"


# ── Error cases ────────────────────────────────────────────────────────────

def test_parse_missing_opening_delimiter():
    with pytest.raises(FrontmatterError, match="missing leading"):
        parse("# No frontmatter\n\nBody only.")


def test_parse_missing_closing_delimiter():
    with pytest.raises(FrontmatterError, match="missing closing"):
        parse("---\nid: x\nowner: y\n")


def test_parse_malformed_yaml():
    content = "---\n  : not\n  valid::\n---\nbody"
    with pytest.raises(FrontmatterError, match="invalid YAML|schema"):
        parse(content)


def test_parse_invalid_status_literal():
    content = "---\nid: x\nowner: y\nstatus: archived\n---\nbody"
    with pytest.raises(FrontmatterError, match="schema"):
        parse(content)


def test_parse_invalid_visibility_literal():
    content = "---\nid: x\nowner: y\nvisibility: secret\n---\nbody"
    with pytest.raises(FrontmatterError, match="schema"):
        parse(content)


def test_parse_missing_required_id():
    content = "---\nowner: y\n---\nbody"
    with pytest.raises(FrontmatterError, match="schema|id"):
        parse(content)


def test_parse_missing_required_owner():
    content = "---\nid: x\n---\nbody"
    with pytest.raises(FrontmatterError, match="schema|owner"):
        parse(content)


def test_parse_yaml_must_be_mapping():
    content = "---\n- just\n- a\n- list\n---\nbody"
    with pytest.raises(FrontmatterError, match="must be a YAML mapping"):
        parse(content)


def test_parse_non_string_input():
    with pytest.raises(FrontmatterError, match="must be a string"):
        parse(b"---\nid: x\n---\n")  # type: ignore[arg-type]


# ── Security ───────────────────────────────────────────────────────────────

def test_parse_rejects_python_object_yaml_tag():
    """yaml.safe_load must refuse Python object construction."""
    content = (
        "---\n"
        "id: x\n"
        "owner: y\n"
        "evil: !!python/object/apply:os.system ['echo pwned']\n"
        "---\nbody"
    )
    with pytest.raises(FrontmatterError):
        parse(content)


def test_parse_rejects_oversized_frontmatter():
    huge = "x: " + ("a" * (16 * 1024 + 100)) + "\n"
    content = f"---\nid: x\nowner: y\n{huge}---\nbody"
    with pytest.raises(FrontmatterError, match="exceeds maximum size"):
        parse(content)


# ── Roundtrip ──────────────────────────────────────────────────────────────

def test_roundtrip_preserves_fields():
    original = """---
id: x
tags: [a, b]
owner: alice
status: published
version: 1.0.0
visibility: private
---

# Hello

World."""
    meta, body = parse(original)
    serialized = serialize(meta, body)
    re_meta, re_body = parse(serialized)
    assert re_meta == meta
    assert "Hello" in re_body
    assert "World" in re_body


def test_roundtrip_with_dates():
    meta = Frontmatter(
        id="x",
        owner="alice",
        tags=["a"],
        status="published",
        visibility="public",
    )
    out = serialize(meta, "Body content")
    re_meta, re_body = parse(out)
    assert re_meta == meta
    assert re_body.strip() == "Body content"


def test_serialize_drops_none_dates():
    meta = Frontmatter(id="x", owner="alice")
    out = serialize(meta, "body")
    assert "created_at" not in out
    assert "updated_at" not in out


# ── Edge cases ─────────────────────────────────────────────────────────────

def test_parse_body_with_internal_triple_dash():
    """A horizontal rule in the body must not be confused with a delimiter."""
    content = "---\nid: x\nowner: y\n---\n\nBefore.\n\n---\n\nAfter."
    meta, body = parse(content)
    assert meta.id == "x"
    assert "Before." in body
    assert "After." in body


def test_parse_extra_fields_preserved():
    content = "---\nid: x\nowner: y\nextra_field: hello\n---\nbody"
    meta, _ = parse(content)
    # extra='allow' on the model preserves unknown keys
    assert getattr(meta, "extra_field", None) == "hello"
