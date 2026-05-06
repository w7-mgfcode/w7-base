import os
import logging
from fastmcp import FastMCP
from mcp_server.api_client import KnowRagApiClient
from mcp_server.features.rag.rag_tools import register_rag_tools
from dotenv import load_dotenv

load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("knowrag-mcp")

# Configuration
API_BASE_URL = os.getenv("API_SERVICE_URL", os.getenv("API_BASE_URL", "http://knowrag-api:8181"))
MCP_PORT = int(os.getenv("MCP_PORT", "8051"))

# MCP Server initialization
mcp = FastMCP(
    "KnowRAG MCP Server"
)

# Initialize API Client
client = KnowRagApiClient(API_BASE_URL)

# Register Features
register_rag_tools(mcp, client)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=MCP_PORT)
