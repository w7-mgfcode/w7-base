import httpx
import logging
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
import asyncio

from urllib.parse import urlparse, urljoin
import re

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
                    "success": True,
                    "raw_html": raw_content if 'xml' not in content_type else ""
                }
        except Exception as e:
            logger.error(f"Crawl failed for {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "success": False
            }

    def extract_links(self, html: str, base_url: str) -> List[str]:
        """
        Extracts internal links from HTML content.
        Filters for same domain/subdomain and ignores non-content extensions.
        """
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        base_parsed = urlparse(base_url)
        internal_links = set()
        
        # Common non-content extensions to ignore
        ignore_ext = re.compile(r'\.(pdf|zip|gz|tar|mp3|mp4|avi|mov|jpg|jpeg|png|gif|svg|ico|css|js|woff|woff2|ttf|otf)$', re.IGNORECASE)
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Join with base URL to handle relative links
            full_url = urljoin(base_url, href)
            # Remove fragments
            full_url = full_url.split('#')[0].rstrip('/')
            
            parsed = urlparse(full_url)
            
            # Check if internal (same hostname)
            if parsed.netloc == base_parsed.netloc:
                # Filter out obvious non-content files
                if not ignore_ext.search(parsed.path):
                    internal_links.add(full_url)
                    
        return list(internal_links)

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

    async def parse_llms_txt(self, url: str) -> List[str]:
        """
        Fetches and parses an llms.txt file to extract URLs.
        llms.txt is a markdown file; we extract all absolute or relative links.
        """
        logger.info(f"Parsing llms.txt: {url}")
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers={"User-Agent": self.user_agent}) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                content = response.text
                # Extract markdown links: [text](url)
                links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', content)
                
                # Normalize and filter
                expanded_urls = set()
                for link in links:
                    full_url = urljoin(url, link).split('#')[0].rstrip('/')
                    if full_url.startswith('http'):
                        expanded_urls.add(full_url)
                
                return list(expanded_urls)
        except Exception as e:
            logger.error(f"Failed to parse llms.txt {url}: {str(e)}")
            return []
