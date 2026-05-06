---
id: verify-related-c
owner: w7-mgfcode
tags: [verify, retrieval, related, kb-smoke, mcp]
status: published
version: 0.1.0
visibility: public
---

# Verify related C — MCP round-trip anchor

The third of three related-pane anchor fixtures for the `w7 verify @lab/ll-KNOWRAG` smoke harness. Every artifact in this verify-fixture set carries the `verify` tag plus the `retrieval` tag, which is what gives the related-pane its semantic floor.

This fixture's specific role is to add MCP-flavored content. The KNOWRAG MCP server (`apps/mcp/src/mcp_server/server.py`) exposes a `rag_search_knowledge_base` tool that is a thin HTTP proxy over `POST /api/artifacts/search`. The verify harness's sixth assertion calls that MCP tool over the FastMCP HTTP transport on port 8051 and asserts that at least one hit comes back. If the MCP container is healthy, the API is reachable, and the search endpoint returns hits, the assertion passes.

## Why thin-proxy MCP matters here

If the MCP service ever starts implementing its own KB logic (cache, re-rank, transform), every change to the API contract becomes a multi-service coordination problem. Phase 8's design discipline is to keep MCP as a forwarding layer. The verify harness exercises this discipline: when `rag_search_knowledge_base` returns hits, it proves both the MCP server's HTTP routing is intact AND the upstream API's search path is healthy. A regression in either surface fails the same check.

## Tag overlap with the baseline

Tags on this fixture: `[verify, retrieval, related, kb-smoke, mcp]`. The baseline carries: `[verify, baseline, retrieval, kb-smoke]`. Three tags overlap (`verify`, `retrieval`, `kb-smoke`), giving the related-pane's tag-scoring path a clear signal independent of embedding quality. Even on a degraded embedder, tag overlap alone should keep this fixture in the top-5.

## What to do if this fixture goes stale

Update the body to reflect current Phase 8 wiring (or remove it and update the related-fixtures count assertion in `verify.sh`). Don't let the fixture content drift away from the actual contract — the harness exists to keep the contract honest, and stale fixtures make the harness lie.
