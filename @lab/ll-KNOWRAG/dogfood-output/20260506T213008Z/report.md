# Verify Report — @lab/ll-KNOWRAG

**Started:** 2026-05-06T21:30:08Z  
**Finished:** 2026-05-06T21:31:10Z  
**Result:** FAIL (exit code 1)

## Summary

| Critical | High | Medium | Low |
|:---:|:---:|:---:|:---:|
| **0** | **3** | **0** | **0** |

## Checks

| ID | Status | ms | Detail |
|---|---|---:|---|
| api.health | pass | 31 | API healthy at http://localhost:8181 |
| gitea.kb_repo_exists | pass | 37 | KB repo exists: knowrag/kb-default |
| ingestion.seed_and_grow | fail | 61952 | Qdrant did not grow within 60s (pre=0, target>0) |
| search.api_returns_hits | fail | 77 | search returned 0 hits |
| related.api_returns_3_plus | fail | 81 | /related returned 0 (need ≥3) |
| mcp.search_returns_hits | pass | 154 | MCP rag_search_knowledge_base responded with valid result |
