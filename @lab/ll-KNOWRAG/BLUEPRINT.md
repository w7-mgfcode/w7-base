# ll-KNOWRAG Blueprint

## 1. Purpose

This repository will become a local-first knowledge-base and RAG system built on:

- local Supabase
- a KB API service
- a KB MCP service
- a KB UI service

The project must actively reuse the KB/RAG core from the Archon repository, while removing product-specific modules that are not required for this system.

This is an extraction-and-adaptation project, not a greenfield rewrite.

## 2. Source Of Truth

### Local repo facts

- The current workspace contains only `_kb/`.
- `_kb/` defines W7-Base operational context, local-first deployment assumptions, and disciplined staged execution.
- `_kb/` does not define an existing application, schema, or implementation for this KB/RAG system.

### Mandatory reuse baseline

The Archon repository is the reference implementation for:

- crawling and discovery
- ingestion orchestration
- source -> page -> chunk storage
- embedding abstraction and batching
- retrieval orchestration
- KB API surface
- MCP tool surface for KB access

## 3. Product Goal

Build a reusable local knowledge platform that can:

- ingest websites and uploaded documents
- discover `llms.txt`, `llms-full.txt`, `sitemap.xml`, and related crawl targets
- store sources, pages, and chunks in local Supabase
- generate embeddings through a provider abstraction
- query by vector search, with optional hybrid search
- return either chunk-level or page-level retrieval results
- expose the KB through:
  - a browser UI
  - an MCP server for agent/tool use

## 4. Non-Goals

The following Archon modules are out of scope for v1 and must not be carried over unless later required:

- projects
- tasks
- document/version management unrelated to KB pages
- prompts table and prompt-builder flows
- agent work orders
- bug-report product features
- MCP dashboards or session UIs beyond basic health/config

## 5. Reuse Policy

### Mandatory reuse

The following Archon components must be reused, adapted, or ported:

#### Crawling and discovery

- `python/src/server/services/crawling/discovery_service.py`
- `python/src/server/services/crawling/crawling_service.py`
- `python/src/server/services/crawler_manager.py`

#### Ingestion and storage flow

- `python/src/server/api_routes/knowledge_api.py`
- `python/src/server/services/crawling/document_storage_operations.py`
- `python/src/server/services/crawling/page_storage_operations.py`
- `python/src/server/services/storage/document_storage_service.py`
- `python/src/server/services/source_management_service.py`

#### Retrieval

- `python/src/server/services/search/base_search_strategy.py`
- `python/src/server/services/search/rag_service.py`
- `python/src/server/services/search/hybrid_search_strategy.py`
- `python/src/server/services/search/reranking_strategy.py`
- `python/src/server/api_routes/pages_api.py`

#### Embeddings and provider layer

- `python/src/server/services/embeddings/embedding_service.py`
- `python/src/server/services/embeddings/contextual_embedding_service.py`
- `python/src/server/services/llm_provider_service.py`
- `python/src/server/services/provider_discovery_service.py`

#### MCP

- `python/src/mcp_server/mcp_server.py`
- `python/src/mcp_server/features/rag/rag_tools.py`

#### UI reference patterns

- `archon-ui-main/src/features/knowledge/views/KnowledgeView.tsx`
- `archon-ui-main/src/features/knowledge/components/AddKnowledgeDialog.tsx`
- `archon-ui-main/src/features/knowledge/services/knowledgeService.ts`

### Allowed simplifications

Reuse does not mean copying all complexity unchanged. The following simplifications are required:

- trim schema to KB-focused tables
- trim MCP tools to KB-only tools
- trim provider support in v1 to a smaller subset
- trim deployment topology to only required services
- trim optional retrieval features behind config flags

### Replacement rule

If a reused Archon component is not adopted, the replacement must:

- be explicitly justified
- be simpler or more flexible
- preserve the same or better architectural clarity

## 6. Target Architecture

The target system has three services plus Supabase:

1. `knowrag-api`
2. `knowrag-mcp`
3. `knowrag-ui`
4. `supabase` local stack

### Service roles

#### `knowrag-api`

Owns:

- crawl and upload endpoints
- discovery logic
- ingestion orchestration
- chunking
- embeddings
- source/page/chunk persistence
- RAG retrieval
- page lookup
- source management

#### `knowrag-mcp`

Owns:

- MCP tool registration
- HTTP forwarding to `knowrag-api`
- health and session primitives

It must not reimplement KB logic internally.

#### `knowrag-ui`

Owns:

- adding knowledge by URL or file
- listing sources
- progress display
- source inspection
- page/chunk browsing
- search and retrieval interaction

#### `supabase`

Owns:

- PostgreSQL storage
- pgvector
- trigram/full-text support
- auth role enforcement where needed

## 7. Recommended Repository Structure

```text
.
├── BLUEPRINT.md
├── _kb/
├── compose.yml
├── .env.example
├── apps/
│   ├── api/
│   │   ├── src/
│   │   │   ├── server/
│   │   │   │   ├── api_routes/
│   │   │   │   ├── services/
│   │   │   │   │   ├── crawling/
│   │   │   │   │   ├── embeddings/
│   │   │   │   │   ├── knowledge/
│   │   │   │   │   ├── search/
│   │   │   │   │   └── storage/
│   │   │   │   ├── config/
│   │   │   │   ├── models/
│   │   │   │   └── utils/
│   │   ├── tests/
│   │   └── Dockerfile
│   ├── mcp/
│   │   ├── src/
│   │   │   ├── mcp_server/
│   │   │   │   ├── features/
│   │   │   │   │   └── rag/
│   │   │   │   └── utils/
│   │   └── Dockerfile
│   └── ui/
│       ├── src/
│       │   ├── features/
│       │   │   ├── knowledge/
│       │   │   ├── progress/
│       │   │   └── shared/
│       └── Dockerfile
├── db/
│   ├── migrations/
│   │   ├── 001_extensions.sql
│   │   ├── 002_settings.sql
│   │   ├── 003_kb_sources.sql
│   │   ├── 004_kb_pages.sql
│   │   ├── 005_kb_chunks.sql
│   │   ├── 006_search_functions.sql
│   │   └── 007_optional_code_examples.sql
│   └── seeds/
└── docs/
    ├── archon-porting-map.md
    ├── api-contracts.md
    ├── schema.md
    └── runbook.md
```

## 8. Archon Porting Map

### Port directly with minimal change

- `discovery_service.py`
  - keep discovery priority order
  - keep SSRF protections
  - keep `llms.txt` and sitemap handling

- `crawler_manager.py`
  - keep Crawl4AI initialization pattern
  - remove Archon-specific log noise only

- `crawling_service.py`
  - keep crawl mode selection:
    - text/markdown
    - sitemap
    - recursive page crawl
    - discovered-file mode
  - keep progress mapping concept
  - keep cancellation support

- `page_storage_operations.py`
  - keep page-first storage
  - keep `llms-full.txt` section splitting behavior

- `base_search_strategy.py`
  - keep RPC-based vector search pattern

- `rag_service.py`
  - keep coordinator pattern:
    - vector
    - optional hybrid
    - optional reranking
    - page grouping mode

- `mcp_server.py`
  - keep separate MCP service/process
  - keep FastMCP pattern
  - remove non-KB modules

- `rag_tools.py`
  - keep KB-focused MCP tools
  - repoint to new API URLs

### Port with simplification

- `knowledge_api.py`
  - keep endpoint structure and background job shape
  - remove project/task/product coupling
  - reduce to KB operations only

- `document_storage_operations.py`
  - keep source -> page -> chunk ordering
  - simplify source metadata generation
  - tighten chunk sizing strategy

- `document_storage_service.py`
  - keep batch embedding and batch insert flow
  - simplify config surface
  - remove optional complexity that does not affect correctness

- `embedding_service.py`
  - keep provider adapter interface
  - keep batch result object and partial-failure handling
  - reduce provider matrix in v1

- `llm_provider_service.py`
  - keep OpenAI-compatible client abstraction
  - reduce supported providers initially

- `provider_discovery_service.py`
  - keep only if dynamic provider/model inspection is needed in v1
  - otherwise defer to phase 2

### Do not port for v1

- project tools
- task tools
- document builder/product docs system
- feature tools
- version tools unrelated to KB pages
- agent work orders

## 9. Data Model

The required model is:

- source
  - one ingest origin
  - one refresh boundary
  - one user-visible knowledge item
- page
  - one full retrievable document or section
  - parented by source
- chunk
  - one embedding/search unit
  - parented by page and source

### Required tables

#### `kb_settings`

Purpose:

- runtime config
- provider config
- RAG feature flags

Minimum fields:

- `id uuid pk`
- `key text unique not null`
- `value text`
- `encrypted_value text`
- `is_encrypted boolean`
- `category text`
- `description text`
- `created_at timestamptz`
- `updated_at timestamptz`

#### `kb_sources`

Purpose:

- source registry
- refresh anchor
- UI listing unit

Minimum fields:

- `source_id text pk`
- `source_url text`
- `source_display_name text`
- `title text`
- `summary text`
- `metadata jsonb default '{}'`
- `total_word_count integer default 0`
- `created_at timestamptz`
- `updated_at timestamptz`

Metadata should include:

- `knowledge_type`
- `tags`
- `source_type`
- `update_frequency`
- `original_url`

#### `kb_pages`

Purpose:

- full-page retrieval
- page-mode RAG
- section-aware navigation

Minimum fields:

- `id uuid pk`
- `source_id text not null references kb_sources(source_id) on delete cascade`
- `url text unique not null`
- `full_content text not null`
- `section_title text null`
- `section_order integer default 0`
- `word_count integer not null`
- `char_count integer not null`
- `chunk_count integer default 0`
- `metadata jsonb default '{}'`
- `created_at timestamptz`
- `updated_at timestamptz`

#### `kb_chunks`

Purpose:

- semantic retrieval unit
- hybrid retrieval unit

Minimum fields:

- `id bigserial pk`
- `source_id text not null references kb_sources(source_id) on delete cascade`
- `page_id uuid null references kb_pages(id) on delete set null`
- `url text not null`
- `chunk_number integer not null`
- `content text not null`
- `metadata jsonb default '{}'`
- `embedding vector(1536)` for v1 default if using OpenAI-compatible 1536-dim model
- `embedding_model text`
- `embedding_dimension integer`
- `llm_chat_model text`
- `content_search_vector tsvector generated always as (...) stored`
- `created_at timestamptz`
- `unique(url, chunk_number)`

#### `kb_code_examples` optional

Purpose:

- code-example extraction
- code-search mode

This is phase 2 unless explicitly needed in v1.

### Extensions

Required:

- `vector`
- `pgcrypto`
- `pg_trgm`

### Indexes

Required:

- GIN on `kb_sources.metadata`
- GIN on `kb_pages.metadata`
- GIN on `kb_chunks.metadata`
- IVFFLAT on `kb_chunks.embedding`
- GIN on `kb_chunks.content_search_vector`
- GIN trigram on `kb_chunks.content`
- btree on `kb_chunks.source_id`
- btree on `kb_chunks.page_id`

## 10. Chunking Strategy

Archon currently chunks with `smart_chunk_text_async(..., chunk_size=5000)` in the storage flow.

### Blueprint decision

Do not keep the 5000-character default unchanged for v1 retrieval.

### Justification

The Archon flow is worth reusing, but the chunk size should be stricter for better retrieval precision. For a KB-first system, smaller structured chunks are better than large broad chunks.

### v1 chunking rules

Use a two-stage chunker:

1. structural split
   - split on headings
   - split on section boundaries
   - preserve source URL and section info

2. fallback windowing
   - target 1200 to 1800 characters
   - overlap 150 to 250 characters

For `llms-full.txt`:

- keep Archon’s section-page strategy
- then chunk within section

For PDFs and uploaded docs:

- normalize to text first
- chunk by heading or paragraph if available
- fallback to windowing

## 11. Ingestion Flow

The ingestion flow must follow the Archon sequence.

### Canonical ingestion pipeline

1. validate request
2. validate provider/API availability if needed
3. initialize progress tracker
4. discover related crawl target
   - `llms.txt`
   - `llms-full.txt`
   - `sitemap.xml`
   - `robots.txt`
5. select crawl mode
   - single page
   - recursive page crawl
   - sitemap crawl
   - text-file crawl
6. crawl content
7. create or upsert source record
8. store full pages
9. generate chunks
10. generate embeddings in batches
11. store chunks
12. optionally extract/store code examples
13. mark operation complete

### Upload flow

Use the same ingestion backbone for uploaded documents:

1. upload file
2. extract text
3. create source
4. store page
5. chunk
6. embed
7. store chunks

## 12. Embedding Layer

### Required reuse

Port the abstraction pattern from Archon:

- provider adapter interface
- single-item wrapper over batch embeddings
- partial-failure batch result
- provider-aware model selection

### v1 provider support

Support only:

- `ollama`
- one OpenAI-compatible provider

Good choices:

- local: `ollama`
- cloud/OpenAI-compatible: `openai` or `openrouter`

### Deferred providers

Do not implement in v1 unless explicitly needed:

- google
- anthropic direct
- grok

### Embedding behavior

- embedding generation must be batched
- batch failures must not corrupt stored rows
- no zero-vector fallback
- failed embeddings stay out of `kb_chunks`

## 13. Retrieval Layer

### v1 required

- vector search
- page-mode return
- source filtering

### v1 optional but planned

- hybrid search
- reranking

### Retrieval coordinator

Keep Archon’s layered orchestration:

1. embed query
2. vector search
3. optional hybrid merge
4. optional rerank
5. optional page grouping

### Search functions

Implement DB RPCs analogous to Archon, renamed for this project:

- `match_kb_chunks`
- `hybrid_search_kb_chunks`
- optional `match_kb_code_examples`

### Page mode

Keep the Archon concept:

- rank chunks
- group them by `page_id` or URL
- return page summaries
- expose a separate endpoint to fetch full page content

## 14. API Blueprint

The API must follow Archon’s KB surface, trimmed to KB-only operations.

### Required endpoints

#### Knowledge operations

- `POST /api/knowledge-items/crawl`
- `POST /api/documents/upload`
- `GET /api/crawl-progress/{progress_id}`
- `POST /api/knowledge-items/stop/{progress_id}`
- `GET /api/knowledge-items`
- `GET /api/knowledge-items/summary`
- `PUT /api/knowledge-items/{source_id}`
- `DELETE /api/knowledge-items/{source_id}`
- `POST /api/knowledge-items/{source_id}/refresh`

#### Inspection

- `GET /api/knowledge-items/{source_id}/chunks`
- `GET /api/knowledge-items/{source_id}/code-examples` optional
- `GET /api/rag/sources`

#### RAG

- `POST /api/rag/query`
- `POST /api/rag/code-examples` optional

#### Pages

- `GET /api/pages`
- `GET /api/pages/{page_id}`
- `GET /api/pages/by-url`

#### Health

- `GET /health`
- `GET /api/health`

### API contract principles

- background jobs for crawl/upload
- progress polling support
- deterministic response shapes
- source IDs, not domain strings, for filtering
- page retrieval separated from search

## 15. MCP Blueprint

### Architecture

Keep Archon’s model:

- separate MCP service
- FastMCP
- tools call API over HTTP

### Required MCP tools

- `health_check`
- `session_info`
- `rag_get_available_sources`
- `rag_search_knowledge_base`
- `rag_list_pages_for_source`
- `rag_read_full_page`

Optional:

- `rag_search_code_examples`
- `kb_refresh_source`
- `kb_delete_source`
- `kb_start_crawl`
- `kb_upload_document`

### Tools to remove

- project tools
- task tools
- document management tools unrelated to KB pages
- feature/version/product tools

### MCP instructions

The MCP instructions should be rewritten for this project, but keep Archon’s operational guidance:

- search sources first
- use `source_id`
- keep search queries focused
- prefer page-mode for context
- use page-read after page search

## 16. UI Blueprint

Use Archon’s knowledge UI as the reference pattern.

### Required screens/components

#### Main view

- list of sources
- search box
- knowledge-type filter
- grid/table toggle
- active operations panel

#### Add knowledge dialog

- crawl URL tab
- upload file tab
- tags
- knowledge type
- crawl depth

#### Inspector

- source summary
- pages
- chunks
- code examples optional

#### Search experience

- query box
- source filter dropdown
- return mode switch:
  - chunks
  - pages
- result inspection

### UI exclusions

Do not port:

- projects
- tasks
- work orders
- product-specific dashboards

## 17. Compose Topology

### Required services

- `knowrag-api`
- `knowrag-mcp`
- `knowrag-ui`
- local Supabase stack

### Suggested compose shape

```yaml
services:
  knowrag-api:
    build: ./apps/api
    environment:
      - SUPABASE_URL=http://host.docker.internal:8000
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - API_PORT=8181
    ports:
      - "8181:8181"

  knowrag-mcp:
    build: ./apps/mcp
    environment:
      - API_SERVICE_URL=http://knowrag-api:8181
      - MCP_PORT=8051
    ports:
      - "8051:8051"
    depends_on:
      - knowrag-api

  knowrag-ui:
    build: ./apps/ui
    environment:
      - VITE_API_BASE=/api
    ports:
      - "3737:3737"
    depends_on:
      - knowrag-api
```

### Local Supabase note

Use the official local Supabase stack outside or alongside the app compose, but the app blueprint assumes:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`

are wired into the API and MCP services.

## 18. Configuration Surface

### `.env.example`

Required variables:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `HOST`
- `API_PORT`
- `MCP_PORT`
- `UI_PORT`
- `LLM_PROVIDER`
- `LLM_BASE_URL`
- `EMBEDDING_PROVIDER`
- `EMBEDDING_MODEL`
- `CHAT_MODEL`
- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `OLLAMA_BASE_URL`
- `USE_HYBRID_SEARCH`
- `USE_RERANKING`
- `USE_CONTEXTUAL_EMBEDDINGS`
- `ENABLE_CODE_EXAMPLES`
- `CRAWL_MAX_CONCURRENT`
- `CRAWL_BATCH_SIZE`
- `CRAWL_PAGE_TIMEOUT`
- `CRAWL_WAIT_STRATEGY`

### Settings ownership

v1 recommendation:

- keep secrets in `.env`
- keep runtime flags in DB-backed `kb_settings`

Reason:

- mirrors the useful part of Archon
- keeps runtime tuning flexible
- avoids overloading env configuration

## 19. Security Requirements

Carry over these ideas from Archon:

- service-role key only for backend/MCP services
- no anon key for write paths
- SSRF protections in discovery
- no Docker socket requirement for MCP health by default
- clear separation of API and MCP process

Additional v1 rules:

- uploads must enforce size limits
- crawler must restrict unsafe targets
- logs must not leak provider keys
- chunk insert path must reject missing `source_id`

## 20. Testing Blueprint

### Unit tests

- discovery URL selection
- chunking behavior
- embedding batch partial failure
- vector search formatting
- page grouping logic
- source deletion cascade behavior

### Integration tests

- crawl URL -> source/pages/chunks stored
- upload document -> source/pages/chunks stored
- RAG query chunk mode
- RAG query page mode
- page fetch by id/url
- MCP tool -> API roundtrip

### UI tests

- open add dialog
- start crawl
- poll progress
- list sources
- inspect chunks/pages
- run search

## 21. Implementation Slices

### Slice 1: Repo foundation

Deliver:

- repo structure
- `compose.yml`
- `.env.example`
- app scaffolds
- migration folder

Acceptance:

- services boot with placeholder health endpoints

### Slice 2: Schema and source/page/chunk model

Deliver:

- extensions
- `kb_settings`
- `kb_sources`
- `kb_pages`
- `kb_chunks`
- vector search RPC

Acceptance:

- source/page/chunk insertion works end to end

### Slice 3: Crawl/discovery port

Deliver:

- discovery service port
- crawler manager port
- crawl orchestration port
- progress polling

Acceptance:

- crawl a docs site
- discover `llms.txt` or sitemap when present

### Slice 4: Ingestion and embeddings

Deliver:

- source/page/chunk storage sequencing
- embedding provider abstraction
- batch embeddings
- upload flow

Acceptance:

- crawl and upload both populate retrievable chunks

### Slice 5: Retrieval

Deliver:

- vector query
- page-mode grouping
- pages API

Acceptance:

- query returns relevant chunks and pages

### Slice 6: MCP

Deliver:

- MCP service
- KB tools only

Acceptance:

- MCP client can search sources, query KB, and read full pages

### Slice 7: UI

Deliver:

- knowledge list
- add knowledge
- progress
- inspector
- search view

Acceptance:

- UI supports full basic operator workflow

### Slice 8: Optional retrieval enhancements

Deliver:

- hybrid search
- reranking
- code examples optional

Acceptance:

- feature flags can enable each enhancement independently

## 22. Final Design Decisions

### Decision: include MCP

Yes. Mandatory.

Reason:

- the project explicitly needs KB access through agents/tools
- Archon already provides the right thin-MCP pattern

### Decision: keep source -> page -> chunk

Yes. Mandatory.

Reason:

- it is the best reusable core from Archon
- it supports both retrieval precision and full-page context

### Decision: use a separate MCP service

Yes.

Reason:

- matches Archon’s boundary
- prevents logic duplication
- keeps API as the single knowledge engine

### Decision: simplify the schema

Yes.

Reason:

- Archon’s full schema includes product modules this repo does not need

### Decision: simplify provider support in v1

Yes.

Reason:

- reuse the abstraction, not the full matrix

## 23. Build Standard

The implementation is correct only if:

- Archon KB/RAG components are visibly ported or adapted
- no major KB subsystem is rewritten from scratch without justification
- the source -> page -> chunk model is preserved
- MCP exists and is functional
- local Supabase is the primary store
- crawl/discovery behavior includes `llms.txt` and sitemap handling
- retrieval supports chunk mode and page mode

## 24. Immediate Next Step

The next executable step after this blueprint is:

1. create the repo scaffold
2. add the trimmed schema migrations
3. port Archon discovery + crawl manager + crawl orchestration
4. port source/page/chunk storage flow

That is the minimum correct starting sequence for this repository.
