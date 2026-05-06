# Intent Gate

**Classification:** `lifecycle` -> `team-assemble` -> `plan`

## Objective Analysis
The user wants to build a "100% private self-hosted Claude-Code-Agents-style knowledgebase stack" (KNOWRAG). This is a comprehensive application development task involving:
1. **Gitea Integration**: Git-based source of truth for prompts, commands, MCP, etc.
2. **Catalog UI**: React/Svelte/Vue card-based frontend with filters and copy-to-clipboard.
3. **Semantic Search**: Qdrant-backed vector search and similarity.
4. **Ingestion Pipeline**: Automated sync from Git repo structure to Qdrant.
5. **Metadata & Status**: Fields for tags, versions, owners, and visibility.
6. **Deployment**: Dockerized orchestration for small VPS/laptop.

## Missing Constraints & Acceptance Criteria
- **UI Tech Stack**: Preferred frontend framework (React, Vue, Svelte, or Vanilla JS)?
- **Embedding Provider**: Since it's "100% private", should we default to a local Ollama instance for embedding generation, or another local engine (like localai or tei)?
- **Ingestion Trigger**: Should the sync to Qdrant be real-time via Gitea Webhooks or a periodic background task?
- **Metadata Schema**: Are the metadata fields (tags, status, etc.) stored within the Git files (frontmatter) or in a sidecar database/YAML?
- **Open WebUI**: Is it a mandatory core component or just a "nice-to-have" optional wrapper?

## Routing Decision
- **Depth Detected**: `high`
- **Workflow State**: `interviewing`
- **Next Command**: `/omg:interview --intent="Build a 100% private self-hosted KNOWRAG stack"`

## First Socratic Question
"Since the platform must be 100% private and self-hosted, do you have a preferred local inference server (like Ollama) for generating the vector embeddings, and should the ingestion pipeline be triggered automatically by Gitea Webhooks or as a manual background task?"
