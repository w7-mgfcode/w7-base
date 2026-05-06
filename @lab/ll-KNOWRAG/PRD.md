# Product Requirements Document: KNOWRAG Stack

## 1. Problem Statement
Individuals and small teams using private AI coding agents (such as Claude Code, OmG, or similar workflows) lack a centralized, private, and searchable repository for their AI assets. Currently, prompts, commands, MCP server configs, hooks, skills, and raw knowledge files are scattered or hard to discover. 

A self-hosted, lightweight stack is needed to manage, index, and discover these AI assets natively, using a Git repository as the definitive Source of Truth (SoT) while providing a robust semantic search and catalog UI to streamline agent interactions.

## 2. Scope
### In-Scope
*   **Infrastructure:** A 100% private, self-hosted Dockerized stack optimized for small VPS or laptops (e.g., `docker-compose.yml`).
*   **Source of Truth:** Gitea repository enforcing a specific folder structure (`/prompts`, `/commands`, `/mcp`, `/hooks`, `/skills`, `/knowledge`).
*   **Vector Database:** Qdrant integration for storing embeddings.
*   **Ingestion Pipeline:** Automated mechanism to parse Git commits, extract metadata (YAML frontmatter), generate embeddings, and update Qdrant and the UI database.
*   **Catalog UI:** Custom web interface featuring:
    *   Card-based asset display.
    *   Filtering by metadata (tags, status, version, owner, visibility).
    *   1-click "Copy to Clipboard" for asset contents.
    *   Semantic search bar.
    *   "Related/Similar items" discovery section via Qdrant similarity search.
*   **Optional Integration:** Open WebUI support/compatibility.

### Non-Goals
*   **Multi-tenant SaaS:** The system is built for single-tenant or small trusted teams; complex multi-org RBAC is out of scope.
*   **LLM Hosting/Inference:** KNOWRAG will not host the LLM generating the responses. It is strictly an asset catalog and knowledgebase.
*   **Native Agent Execution:** The UI will not execute the agent commands or skills directly; it serves as the discovery and clipboard tool for the developer.
*   **Real-time Collaborative Editing UI:** Editing happens via standard Git workflows (local IDE push to Gitea or Gitea web editor). The custom UI is strictly read-only/discovery-focused.

## 3. Acceptance Criteria
*   **AC1 (Deployment):** Running `docker compose up -d` provisions the entire stack (Gitea, Qdrant, UI, Ingestion worker) on a standard Ubuntu VPS or laptop without manual dependency installation, operating within a 4GB RAM footprint limit.
*   **AC2 (Git SSoT):** The ingestion pipeline successfully reads from a predefined repository structure containing markdown (`.md`) files with YAML frontmatter.
*   **AC3 (Ingestion Automation):** Pushing a new `.md` file to the main branch of the target Gitea repo triggers the ingestion pipeline, extracting metadata (tags, status, version, owner, visibility) and updating Qdrant/UI data within 60 seconds.
*   **AC4 (Catalog UI - Listing):** The web application displays ingested assets as individual cards, allowing Boolean filtering by tags, asset type (prompt/skill/mcp/etc.), and status.
*   **AC5 (Catalog UI - Interaction):** Every asset card includes a functional "Copy to Clipboard" button that accurately copies the raw asset payload to the user's OS clipboard.
*   **AC6 (Semantic Search):** The UI features a search bar that queries Qdrant. A query for "database backup" must return the "pg-dump-script" asset even if the exact keywords "database backup" are missing from the asset's text.
*   **AC7 (Related Items):** Navigating to an individual asset's detail view successfully queries Qdrant to display the Top 3 most semantically similar assets in a "Related" section.

## 4. Constraints and Dependencies
### Technical Constraints
*   **Resource Footprint:** Target environment is small VPS/laptops. Total idle memory usage of the stack (excluding OS) must not exceed 2.5GB.
*   **Embedding Generation:** The ingestion pipeline must use a lightweight local embedding model (e.g., `all-MiniLM-L6-v2` via standard Python libraries) to avoid reliance on external APIs like OpenAI, ensuring 100% privacy.
*   **Deployment Medium:** Must be contained entirely within Docker Compose networks. No external cloud databases or hosted services.

### Dependencies
*   **Gitea Webhooks/Polling:** The ingestion pipeline depends on reliable triggers from Gitea upon repository updates.
*   **Docker Engine:** Target host must have Docker and Docker Compose V2 installed.

## 5. Handoff Checklist
*   [ ] **Architecture:** Architecture component diagram and network flow confirmed.
*   [ ] **Schema:** YAML frontmatter schema (required and optional fields) strictly defined and documented.
*   [ ] **Repository:** Base Git repository structure template created (`/prompts`, `/skills`, etc.).
*   [ ] **Infrastructure:** `docker-compose.yml` base template scaffolded containing Gitea, Qdrant, UI, and Ingestion service stubs.
*   [ ] **Execution:** Assigned to `omg-executor` to begin implementation of the Docker network and UI scaffolding.
*   [ ] **Verification:** Assigned to `omg-verifier` to test AC1-AC7 once the prototype is built.