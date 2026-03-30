# KnowRAG API Contracts

## Knowledge Management
- `GET /api/knowledge-items`: List all sources
- `POST /api/knowledge-items/crawl`: Start a crawl job
- `GET /api/knowledge-items/crawl-progress/{id}`: Check crawl status
- `DELETE /api/knowledge-items/{id}`: Delete a source

## RAG
- `POST /api/rag/query`: Execute search (chunk or page mode)

## Pages
- `GET /api/pages`: List pages (optional source filter)
- `GET /api/pages/{id}`: Get full page content

## Health
- `GET /health`: API health status

# MCP Tools
- `health_check`: System health
- `get_available_sources`: List sources
- `search_knowledge_base`: Semantic search
- `list_pages_for_source`: List pages by source
- `read_page_context`: Fetch full page
- `start_crawl_job`: Trigger ingestion
