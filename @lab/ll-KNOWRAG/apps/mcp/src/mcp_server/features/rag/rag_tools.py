import logging
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from mcp_server.api_client import KnowRagApiClient

logger = logging.getLogger(__name__)

def register_rag_tools(mcp: FastMCP, client: KnowRagApiClient):
    """
    Registers KB/RAG focused tools to the MCP server.
    Ported from Archon: thin forwarding to knowrag-api.
    """

    @mcp.tool()
    async def health_check() -> str:
        """
        Check the health status of the KnowRAG system.
        """
        try:
            health = await client.get_health()
            return f"KnowRAG System Health: {health.get('status', 'unknown')}"
        except Exception as e:
            return f"Error connecting to KnowRAG API: {str(e)}"

    @mcp.tool()
    async def session_info() -> str:
        """
        Returns MCP server session information including API connectivity details.
        """
        return (
            f"KnowRAG MCP Server\n"
            f"API Base URL: {client.base_url}\n"
            f"Transport: HTTP/SSE\n"
            f"Tools: health_check, session_info, rag_get_available_sources, "
            f"rag_search_knowledge_base, rag_list_pages_for_source, rag_read_full_page, start_crawl_job"
        )

    @mcp.tool()
    async def rag_get_available_sources() -> str:
        """
        List all available knowledge sources in the database.
        """
        try:
            sources = await client.list_sources()
            if not sources:
                return "No knowledge sources found."

            output = "Available Knowledge Sources:\n"
            for s in sources:
                output += f"- {s['source_id']}: {s.get('title', 'No Title')} ({s.get('source_url', 'No URL')})\n"
            return output
        except Exception as e:
            return f"Error listing sources: {str(e)}"

    @mcp.tool()
    async def rag_search_knowledge_base(query: str, mode: str = "chunk", limit: int = 5) -> str:
        """
        Search the knowledge base for relevant information.
        - mode: 'chunk' for semantic snippets, 'page' for grouped documents.
        """
        try:
            results = await client.search_kb(query, mode=mode, limit=limit)

            if not results['results']:
                return f"No results found for query: {query}"

            output = f"Search Results for '{query}' ({mode} mode):\n\n"
            for i, res in enumerate(results['results']):
                output += f"--- Result {i+1} ---\n"
                if mode == "chunk":
                    output += f"Content: {res['content']}\n"
                    output += f"Source: {res['source_id']}\n"
                else:
                    output += f"Page: {res['title'] or res['url']}\n"
                    output += f"Source: {res['source_id']}\n"
                    output += f"Snippet: {res['chunks'][0]['content'][:200]}...\n"
                output += "\n"
            return output
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"

    @mcp.tool()
    async def rag_list_pages_for_source(source_id: str) -> str:
        """
        List all pages/documents belonging to a specific source.
        """
        try:
            pages = await client.list_pages(source_id=source_id)
            if not pages:
                return f"No pages found for source: {source_id}"

            output = f"Pages for Source '{source_id}':\n"
            for p in pages:
                output += f"- {p['id']}: {p.get('section_title') or p['url']}\n"
            return output
        except Exception as e:
            return f"Error listing pages: {str(e)}"

    @mcp.tool()
    async def rag_read_full_page(page_id: str) -> str:
        """
        Retrieve the full content of a specific page/document.
        """
        try:
            page = await client.get_page(page_id)
            output = f"--- Page Content ---\n"
            output += f"URL: {page['url']}\n"
            output += f"Title: {page.get('section_title') or 'Untitled'}\n\n"
            output += page['full_content']
            return output
        except Exception as e:
            return f"Error reading page: {str(e)}"

    @mcp.tool()
    async def start_crawl_job(url: str, source_id: Optional[str] = None) -> str:
        """
        Initiate a new crawl/ingestion job for a URL.
        """
        try:
            result = await client.start_crawl(url, source_id=source_id)
            return f"Crawl job started. ID: {result['crawl_id']}"
        except Exception as e:
            return f"Error starting crawl job: {str(e)}"
