import asyncio
from unittest.mock import AsyncMock, MagicMock
from fastmcp import FastMCP
from mcp_server.api_client import KnowRagApiClient
from mcp_server.features.rag.rag_tools import register_rag_tools


def _setup():
    """Creates a FastMCP instance with mocked client and registered tools."""
    mcp = FastMCP("test")
    client = MagicMock(spec=KnowRagApiClient)
    client.base_url = "http://test:8181"
    register_rag_tools(mcp, client)
    return mcp, client


def _call(mcp, name, args=None):
    """Calls an MCP tool by name and returns the text result."""
    result = asyncio.run(mcp.call_tool(name, args or {}))
    return result.content[0].text


def test_health_check_returns_status():
    mcp, client = _setup()
    client.get_health = AsyncMock(return_value={"status": "ok"})
    text = _call(mcp, "health_check")
    assert "ok" in text


def test_session_info_includes_base_url():
    mcp, client = _setup()
    text = _call(mcp, "session_info")
    assert "http://test:8181" in text
    assert "KnowRAG MCP Server" in text


def test_rag_get_available_sources_formats_output():
    mcp, client = _setup()
    client.list_sources = AsyncMock(return_value=[
        {"source_id": "docs", "title": "Documentation", "source_url": "https://docs.example.com"},
    ])
    text = _call(mcp, "rag_get_available_sources")
    assert "docs" in text
    assert "Documentation" in text


def test_rag_get_available_sources_empty():
    mcp, client = _setup()
    client.list_sources = AsyncMock(return_value=[])
    text = _call(mcp, "rag_get_available_sources")
    assert "No knowledge sources found" in text


def test_rag_search_knowledge_base_chunk_mode():
    mcp, client = _setup()
    client.search_kb = AsyncMock(return_value={
        "results": [{"content": "hello world", "source_id": "test-src", "similarity": 0.9}],
        "total_results": 1,
    })
    text = _call(mcp, "rag_search_knowledge_base", {"query": "greeting", "mode": "chunk", "limit": 3})
    assert "hello world" in text
    assert "test-src" in text
    client.search_kb.assert_called_once_with("greeting", mode="chunk", limit=3, use_hybrid=False, use_reranking=False)


def test_rag_read_full_page_error_handling():
    mcp, client = _setup()
    client.get_page = AsyncMock(side_effect=Exception("not found"))
    text = _call(mcp, "rag_read_full_page", {"page_id": "bad-id"})
    assert "Error" in text
    assert "not found" in text


def test_start_crawl_job_returns_id():
    mcp, client = _setup()
    client.start_crawl = AsyncMock(return_value={"crawl_id": "abc-123"})
    text = _call(mcp, "start_crawl_job", {"url": "https://example.com"})
    assert "abc-123" in text
