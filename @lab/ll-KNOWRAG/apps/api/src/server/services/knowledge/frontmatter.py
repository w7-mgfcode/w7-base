"""YAML frontmatter parsing for KB markdown artifacts.

Phase 8 contract: every artifact under the Gitea KB repo is a `.md` file with
YAML frontmatter delimited by `---`. The parser enforces a strict Pydantic
schema and rejects malformed or schema-violating inputs.

Security: uses `yaml.safe_load` exclusively (never `yaml.load`) per
`.claude/rules/security-patterns.md`.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

Status = Literal["draft", "review", "published"]
Visibility = Literal["public", "private"]

DELIMITER = "---"
MAX_FRONTMATTER_BYTES = 16 * 1024  # 16 KiB cap on the YAML block


class FrontmatterError(ValueError):
    """Raised when a markdown document's frontmatter cannot be parsed or
    fails schema validation."""


class Frontmatter(BaseModel):
    """Pydantic schema for KB artifact frontmatter.

    Required: ``id``, ``owner``.
    All other fields have safe defaults so legacy/minimal artifacts still parse.
    """

    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)

    id: str = Field(min_length=1, max_length=128)
    owner: str = Field(min_length=1, max_length=128)
    tags: list[str] = Field(default_factory=list)
    status: Status = "draft"
    version: str = Field(default="0.1.0", max_length=64)
    visibility: Visibility = "private"
    created_at: date | None = None
    updated_at: date | None = None


def parse(content: str) -> tuple[Frontmatter, str]:
    """Parse a markdown document with YAML frontmatter.

    Returns ``(frontmatter, body)``. Raises ``FrontmatterError`` on any
    parse, schema, or safety violation.
    """
    if not isinstance(content, str):
        raise FrontmatterError("content must be a string")
    stripped = content.lstrip("﻿")  # tolerate BOM
    if not stripped.startswith(DELIMITER):
        raise FrontmatterError("missing leading '---' delimiter")

    # Strip the leading delimiter line and locate the closing delimiter.
    after_open = stripped[len(DELIMITER):].lstrip("\r").lstrip("\n")
    end_idx = after_open.find(f"\n{DELIMITER}")
    if end_idx == -1:
        # Tolerate a closing delimiter on its own line at the start (no newline before).
        if after_open.startswith(DELIMITER):
            yaml_block = ""
            body = after_open[len(DELIMITER):]
        else:
            raise FrontmatterError("missing closing '---' delimiter")
    else:
        yaml_block = after_open[:end_idx]
        body = after_open[end_idx + len(DELIMITER) + 1:]  # +1 for the leading \n

    if len(yaml_block.encode("utf-8")) > MAX_FRONTMATTER_BYTES:
        raise FrontmatterError(
            f"frontmatter exceeds maximum size of {MAX_FRONTMATTER_BYTES} bytes"
        )

    try:
        meta: Any = yaml.safe_load(yaml_block) if yaml_block.strip() else {}
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"invalid YAML: {exc}") from exc

    if meta is None:
        meta = {}
    if not isinstance(meta, dict):
        raise FrontmatterError("frontmatter must be a YAML mapping (dict)")

    try:
        fm = Frontmatter.model_validate(meta)
    except ValidationError as exc:
        raise FrontmatterError(f"schema violation: {exc}") from exc

    return fm, body.lstrip("\n")


def serialize(meta: Frontmatter, body: str) -> str:
    """Serialize a frontmatter + body back into a markdown document string."""
    payload = meta.model_dump(exclude_none=True, mode="json")
    yaml_block = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    return f"{DELIMITER}\n{yaml_block}{DELIMITER}\n\n{body.lstrip()}\n"


__all__ = ["Frontmatter", "FrontmatterError", "Status", "Visibility", "parse", "serialize"]
