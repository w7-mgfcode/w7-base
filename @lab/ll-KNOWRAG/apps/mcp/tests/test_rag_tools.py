import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import FastMCP

from mcp_server.api_client import KnowRagApiClient
from mcp_server.features.rag.rag_tools import _coerce_str_list, register_rag_tools


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


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, None),
        ("", None),
        ("  ", None),
        (["a", "b"], ["a", "b"]),
        ([1, 2], ["1", "2"]),
        ('["a","b"]', ["a", "b"]),
        ("a,b , c", ["a", "b", "c"]),
        ("solo", ["solo"]),
    ],
)
def test_coerce_str_list_normalizes_inputs(value, expected):
    assert _coerce_str_list(value) == expected
