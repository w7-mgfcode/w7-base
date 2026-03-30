import httpx
import logging
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
import asyncio

logger = logging.getLogger(__name__)

class CrawlerManager:
    """
    Manages the underlying crawling engine.
    Ported from Archon: adapted to use httpx as a baseline for local-first, 
    with hooks for Crawl4AI or similar high-fidelity crawlers.
    """
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.user_agent = "ll-KNOWRAG/1.0 (Local-First KB; +https://github.com/w7-hector/w7-localbase)"

    async def crawl(self, url: str) -> Dict[str, Any]:
        """
        Executes a single-page crawl.
        """
        logger.info(f"Crawling URL: {url}")
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers={"User-Agent": self.user_agent}) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                raw_content = response.text
                content_type = response.headers.get("content-type", "").lower()
                parser = 'lxml' if 'xml' in content_type else 'html.parser'
                soup = BeautifulSoup(raw_content, parser)
                
                # Basic metadata extraction
                title = soup.title.string if soup.title else ""
                
                if content_type.startswith("text/plain"):
                    content = raw_content
                else:
                    content = soup.get_text(separator="\n", strip=True)

                return {
                    "url": str(response.url),
                    "content": content,
                    "title": title.strip() if title else "",
                    "status_code": response.status_code,
                    "success": True
                }
        except Exception as e:
            logger.error(f"Crawl failed for {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "success": False
            }

    async def parse_sitemap(self, sitemap_url: str) -> List[str]:
        """
        Fetches and parses a sitemap.xml to extract URLs.
        """
        logger.info(f"Parsing sitemap: {sitemap_url}")
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers={"User-Agent": self.user_agent}) as client:
                response = await client.get(sitemap_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'lxml-xml')
                urls = [loc.text for loc in soup.find_all('loc')]
                return urls
        except Exception as e:
            logger.error(f"Failed to parse sitemap {sitemap_url}: {str(e)}")
            return []
