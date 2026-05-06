import httpx
import asyncio
import ipaddress
import socket
from typing import List, Optional, Set
from urllib.parse import urlparse, urljoin, urlunparse
import logging
from server.models.discovery import DiscoveryResult, DiscoveryTarget, DiscoveryType

logger = logging.getLogger(__name__)

class DiscoveryService:
    """
    Ports Archon's discovery logic for local-first KB/RAG.
    Focuses on llms.txt, llms-full.txt, and sitemap.xml.
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.user_agent = "ll-KNOWRAG/1.0 (Local-First KB; +https://github.com/w7-hector/w7-localbase)"

    def normalize_url(self, url: str) -> str:
        """
        SSRF-safe normalization and basic validation.
        """
        parsed = urlparse(url)
        if not parsed.scheme:
            url = f"https://{url}"
            parsed = urlparse(url)
            
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}")

        hostname = parsed.hostname
        if not hostname:
            raise ValueError("URL must include a valid hostname")

        try:
            addrinfo = socket.getaddrinfo(hostname, None)
        except socket.gaierror as exc:
            raise ValueError(f"Could not resolve hostname: {hostname}") from exc

        for entry in addrinfo:
            ip = ipaddress.ip_address(entry[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                raise ValueError(f"Refusing to crawl private or local address: {ip}")

        return urlunparse(parsed._replace(fragment="")).rstrip("/")

    async def discover(self, url: str) -> DiscoveryResult:
        """
        Executes discovery on a base URL.
        """
        try:
            canonical_url = self.normalize_url(url)
            targets = []
            
            # 1. Direct candidates (Fast checks)
            candidates = [
                (f"{canonical_url}/llms.txt", DiscoveryType.LLMS_TXT, 100),
                (f"{canonical_url}/.well-known/llms.txt", DiscoveryType.LLMS_TXT, 95),
                (f"{canonical_url}/llms-full.txt", DiscoveryType.LLMS_FULL_TXT, 90),
                (f"{canonical_url}/sitemap.xml", DiscoveryType.SITEMAP_XML, 80),
                (f"{canonical_url}/robots.txt", DiscoveryType.ROBOTS_TXT, 50),
            ]
            
            # Parallel check for existence (HEAD requests)
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers={"User-Agent": self.user_agent}) as client:
                tasks = [self._check_target(client, c[0], c[1], c[2]) for c in candidates]
                results = await asyncio.gather(*tasks)
                targets.extend([r for r in results if r])

            # Always include the base URL as a single page target if no high-priority discovery found
            targets.append(DiscoveryTarget(
                url=canonical_url,
                target_type=DiscoveryType.SINGLE_PAGE,
                priority=10
            ))
            
            # Sort targets by priority
            targets.sort(key=lambda x: x.priority, reverse=True)
            
            return DiscoveryResult(
                base_url=url,
                canonical_url=canonical_url,
                targets=targets
            )
            
        except Exception as e:
            logger.error(f"Discovery failed for {url}: {str(e)}")
            return DiscoveryResult(
                base_url=url,
                canonical_url=url,
                success=False,
                error=str(e)
            )

    async def _check_target(self, client: httpx.AsyncClient, url: str, target_type: DiscoveryType, priority: int) -> Optional[DiscoveryTarget]:
        """
        Checks if a target URL exists and returns a DiscoveryTarget.
        """
        try:
            # We use GET for robots.txt/sitemap/llms.txt to be sure, or HEAD if we want speed
            # Archon uses GET to potentially parse the content immediately
            response = await client.get(url)
            if response.status_code == 200:
                # Basic check for content type if it's supposed to be XML/Text
                content_type = response.headers.get("content-type", "").lower()
                if target_type == DiscoveryType.SITEMAP_XML and "xml" not in content_type and not url.endswith(".xml"):
                     return None
                
                return DiscoveryTarget(
                    url=str(response.url),
                    target_type=target_type,
                    priority=priority,
                    metadata={"content_type": content_type}
                )
        except Exception:
            pass
        return None
