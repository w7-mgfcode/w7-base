# Team Assembly: KNOWRAG Knowledgebase Stack

## Objective
Build a 100% private self-hosted Claude-Code-Agents-style knowledgebase stack (KNOWRAG) with Gitea, custom catalog UI, Qdrant, and optional Open WebUI.

## Roles
- **Orchestration:** `omg-director` (gemini-3.1-pro-preview)
- **Architecture:** `omg-architect` (gemini-3.1-pro-preview)
- **Execution:** `omg-executor` (gemini-3-flash-preview)
- **Quality/Verification:** `omg-verifier` (gemini-3.1-pro-preview)
- **Product/Editorial:** `omg-product` (gemini-3.1-pro-preview)

## Collaboration Protocol
- **Critical Path:** Architecture -> Infrastructure Scaffold -> Backend/Ingestion -> UI.
- **Lane Ownership:** `@lab/ll-KNOWRAG/` workspace.
- **Reasoning Allocation:** Global reasoning override is `high`. Reviewers will use maximum effort.
