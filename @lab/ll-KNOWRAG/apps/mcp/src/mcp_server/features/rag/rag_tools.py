import json
import logging
from typing import List, Dict, Any, Optional, Union

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from mcp_server.api_client import KnowRagApiClient

logger = logging.getLogger(__name__)


def _coerce_str_list(value: Union[str, List[str], None]) -> Optional[List[str]]:
    """Tolerate FastMCP v3 client quirk where list params arrive as a JSON-
    encoded string. Returns ``None`` for empty/None, list otherwise."""
    if value is None:
        return None
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            decoded = json.loads(s)
            if isinstance(decoded, list):
                return [str(v) for v in decoded]
        except (json.JSONDecodeError, ValueError):
            pass
        # Fall back: comma-separated string
        return [p.strip() for p in s.split(",") if p.strip()]
    raise ToolError(f"expected list or string, got {type(value).__name__}")


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
            f"Tools: health_check, session_info, rag_list_artifacts, "
            f"rag_get_artifact, rag_get_related_pages, rag_search_artifacts"
        )

    # ── Gitea-backed artifact tools ────────────────────────────────────────

    @mcp.tool()
    async def rag_list_artifacts(category: Optional[str] = None) -> Dict[str, Any]:
        """List Gitea-backed KB artifacts with their frontmatter metadata.

        When to use:
        - User asks "what artifacts/notes/prompts/skills are in the KB?"
        - Building a catalog or filterable view client-side
        - Need tags/status/owner/version per artifact (not chunk-level data)

        Args:
            category: Optional. One of: prompts, commands, mcp, hooks, skills,
                knowledge. If omitted, returns artifacts across all categories.

        Returns: dict with keys:
            total: int — count of artifacts returned
            items: list of {path, frontmatter: {id, owner, tags, status, version,
                visibility, ...}, commit_sha, size}
        """
        try:
            items = await client.list_artifacts(category=category)
            return {"total": len(items), "items": items}
        except (ValidationError, ValueError) as exc:
            raise ToolError(f"invalid arguments: {exc}")
        except Exception as exc:
            raise ToolError(f"failed to list artifacts: {exc}")

    @mcp.tool()
    async def rag_get_artifact(path: str, ref: Optional[str] = None) -> Dict[str, Any]:
        """Fetch one Gitea-backed artifact (frontmatter + body + commit_sha).

        When to use:
        - User asks to read or summarize a specific artifact by path
        - Need the full markdown body, not just metadata
        - Reading a specific commit/branch (pass ref)

        Args:
            path: Required. Canonical path e.g. "knowledge/x.md" or
                "skills/my-skill.md". Must match <category>/<name>.md.
            ref: Optional. Git ref (branch/tag/commit SHA). Defaults to repo
                default branch.

        Returns: dict with keys: path, frontmatter, body (full markdown
            without frontmatter), commit_sha, size.
        """
        try:
            return await client.get_artifact(path, ref=ref)
        except (ValidationError, ValueError) as exc:
            raise ToolError(f"invalid arguments: {exc}")
        except Exception as exc:
            raise ToolError(f"failed to get artifact {path!r}: {exc}")

    @mcp.tool()
    async def rag_get_related_pages(
        path: str, k: int = 5, visibility: str = "public"
    ) -> Dict[str, Any]:
        """Find artifacts semantically similar to the given one (kNN on Qdrant).

        When to use:
        - User asks "what's related to X?" or "similar to this artifact"
        - Building cross-references between KB artifacts
        - Suggesting next-reads after the user opens an artifact

        Args:
            path: Required. Seed artifact path, e.g. "knowledge/rag-101.md".
            k: Number of related artifacts (1-20, default 5).
            visibility: "public" or "private" — must match the seed
                artifact's visibility scope.

        Returns: dict with keys:
            seed_path: str — the input artifact
            total: int — number of related items
            items: list of {artifact_path, score, section_title, snippet,
                tags, status, owner, shared_tags}
        """
        try:
            if visibility not in ("public", "private"):
                raise ToolError("visibility must be 'public' or 'private'")
            items = await client.related_artifacts(path, k=k, visibility=visibility)
            return {"seed_path": path, "total": len(items), "items": items}
        except (ValidationError, ValueError) as exc:
            raise ToolError(f"invalid arguments: {exc}")
        except ToolError:
            raise
        except Exception as exc:
            raise ToolError(f"failed to find related for {path!r}: {exc}")

    @mcp.tool()
    async def rag_search_artifacts(
        query: str,
        tags: Union[str, List[str], None] = None,
        status: Union[str, List[str], None] = None,
        owner: Optional[str] = None,
        visibility: str = "public",
        top_k: int = 20,
        use_hybrid: bool = False,
        use_rerank: bool = False,
    ) -> Dict[str, Any]:
        """Semantic search across KB artifacts with frontmatter filter pushdown.

        When to use:
        - User asks a question that may be answered by KB content
        - Filtering by tags, status (draft/review/published), or owner before search
        - Building a "search within tag X" experience

        Args:
            query: Required. Free-text natural-language query.
            tags: Optional. Tag filter — list of strings, or a comma-separated
                string, or a JSON-encoded array (any tag matches).
            status: Optional. Status filter — same format as tags.
                Valid values: draft, review, published.
            owner: Optional. Owner exact-match filter.
            visibility: "public" or "private". Default "public".
            top_k: Max results (default 20).
            use_hybrid: Combine vector + BM25 sparse search.
            use_rerank: Apply reranker after retrieval.

        Returns: dict with keys: hits (chunk-level), pages (grouped by
            artifact). Each page entry has artifact_path, top_score, owner,
            tags, chunk_count.
        """
        try:
            tags_list = _coerce_str_list(tags)
            status_list = _coerce_str_list(status)
            if visibility not in ("public", "private"):
                raise ToolError("visibility must be 'public' or 'private'")
            return await client.search_artifacts(
                query=query,
                tags=tags_list,
                status=status_list,
                owner=owner,
                visibility=visibility,
                top_k=top_k,
                use_hybrid=use_hybrid,
                use_rerank=use_rerank,
            )
        except (ValidationError, ValueError) as exc:
            raise ToolError(f"invalid arguments: {exc}")
        except ToolError:
            raise
        except Exception as exc:
            raise ToolError(f"search failed: {exc}")
