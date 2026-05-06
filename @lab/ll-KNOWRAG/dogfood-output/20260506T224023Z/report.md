# Verify Report — @lab/ll-KNOWRAG

**Started:** 2026-05-06T22:40:23Z  
**Finished:** 2026-05-06T22:40:27Z  
**Result:** PASS (exit code 0)

## Summary

| Critical | High | Medium | Low |
|:---:|:---:|:---:|:---:|
| **0** | **0** | **0** | **0** |

## Checks

| ID | Status | ms | Detail |
|---|---|---:|---|
| api.health | pass | 30 | API healthy at http://localhost:8181 |
| gitea.kb_repo_exists | pass | 49 | KB repo exists: knowrag/kb-default |
| ingestion.seed_and_grow | pass | 3319 | seeded 4 artifacts; Qdrant 0 → 10 points |
| search.api_returns_hits | pass | 181 | search returned 10 hits |
| related.api_returns_3_plus | pass | 97 | /related returned 3 sibling artifacts |
| mcp.search_returns_hits | pass | 149 | MCP rag_search_knowledge_base responded with valid result |
