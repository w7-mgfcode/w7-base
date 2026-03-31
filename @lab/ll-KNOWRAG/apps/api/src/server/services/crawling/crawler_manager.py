import httpx
import logging
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
import asyncio
import re
from urllib.parse import urlparse, urljoin

# Conditional import — graceful if crawl4ai not installed
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False

logger = logging.getLogger(__name__)


class CrawlerManager:
    """
    Manages the underlying crawling engine.
    Uses Crawl4AI (headless Chromium) as primary engine with automatic httpx fallback.
    Ported from Archon: adapted for local-first use with graceful degradation.
    """

    def __init__(self, timeout: int = 30, use_crawl4ai: bool = True, **crawl4ai_opts):
        self.timeout = timeout
        self.user_agent = "ll-KNOWRAG/1.0 (Local-First KB; +https://github.com/w7-hector/w7-localbase)"
        self._use_crawl4ai = use_crawl4ai and CRAWL4AI_AVAILABLE
        self._crawler: Optional[Any] = None  # AsyncWebCrawler instance
        self._crawl4ai_opts = crawl4ai_opts
        self._last_links_cache: Dict[str, List[str]] = {}

    async def startup(self):
        """Initialize Chromium browser. Called during FastAPI lifespan startup."""
        if not self._use_crawl4ai:
            logger.info("CrawlerManager: httpx mode (no browser).")
            return
        try:
            browser_config = BrowserConfig(
                headless=self._crawl4ai_opts.get("headless", True),
                viewport_width=self._crawl4ai_opts.get("viewport_width", 1920),
                viewport_height=self._crawl4ai_opts.get("viewport_height", 1080),
                user_agent=self.user_agent,
                browser_type="chromium",
                extra_args=["--no-sandbox", "--disable-dev-shm-usage",
                            "--disable-gpu", "--disable-images"],
            )
            self._crawler = AsyncWebCrawler(config=browser_config)
            await self._crawler.__aenter__()
            logger.info("CrawlerManager: Crawl4AI browser started.")
        except Exception as e:
            logger.error(f"Crawl4AI browser failed to start: {e}. Falling back to httpx.")
            self._crawler = None
            self._use_crawl4ai = False

    async def shutdown(self):
        """Close browser. Called during FastAPI lifespan shutdown."""
        if self._crawler:
            try:
                await self._crawler.__aexit__(None, None, None)
            except Exception:
                pass
            self._crawler = None

    async def crawl(self, url: str) -> Dict[str, Any]:
        """Crawl a single page. Uses Crawl4AI if available, httpx otherwise."""
        if self._crawler:
            return await self._crawl_with_browser(url)
        return await self._crawl_with_httpx(url)

    async def _crawl_with_browser(self, url: str) -> Dict[str, Any]:
        """Crawl4AI browser-based fetch. Returns same dict contract as httpx path."""
        logger.info(f"Crawling (browser): {url}")
        try:
            run_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                wait_until=self._crawl4ai_opts.get("wait_strategy", "networkidle"),
                page_timeout=self.timeout * 1000,  # Crawl4AI uses ms
                delay_before_return_html=self._crawl4ai_opts.get("delay_before_return", 1.0),
                scan_full_page=self._crawl4ai_opts.get("scan_full_page", True),
            )
            result = await self._crawler.arun(url=url, config=run_config)

            if not result.success:
                return {"url": url, "error": result.error_message or "Crawl failed", "success": False}

            # Title from HTML (Archon pattern)
            title = ""
            if result.html:
                m = re.search(r"<title[^>]*>(.*?)</title>", result.html, re.IGNORECASE | re.DOTALL)
                if m:
                    title = m.group(1).strip()

            # Cache internal links for extract_links() (consumed on read)
            if hasattr(result, "links") and isinstance(result.links, dict):
                self._last_links_cache[url] = [
                    link["href"] for link in result.links.get("internal", [])
                    if link.get("href")
                ]

            return {
                "url": url,
                "content": result.markdown or "",
                "title": title,
                "status_code": getattr(result, "status_code", 200) or 200,
                "success": True,
                "raw_html": result.html or "",
            }
        except Exception as e:
            logger.error(f"Browser crawl failed for {url}: {e}")
            return {"url": url, "error": str(e), "success": False}

    async def _crawl_with_httpx(self, url: str) -> Dict[str, Any]:
        """Original httpx-based fetch. Preserved as fallback."""
        logger.info(f"Crawling (httpx): {url}")
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
        Uses cached Crawl4AI links if available, else BeautifulSoup.
        """
        # Try Crawl4AI cache first (populated during _crawl_with_browser)
        cached = self._last_links_cache.pop(base_url, None)
        if cached:
            base_parsed = urlparse(base_url)
            ignore_ext = re.compile(
                r'\.(pdf|zip|gz|tar|mp3|mp4|avi|mov|jpg|jpeg|png|gif|svg|ico|css|js|woff|woff2|ttf|otf)$',
                re.IGNORECASE
            )
            filtered = set()
            for link in cached:
                clean = link.split('#')[0].rstrip('/')
                parsed = urlparse(clean)
                if parsed.netloc == base_parsed.netloc and not ignore_ext.search(parsed.path):
                    filtered.add(clean)
            return list(filtered)

        # Fallback: BeautifulSoup extraction
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        base_parsed = urlparse(base_url)
        internal_links = set()

        ignore_ext = re.compile(
            r'\.(pdf|zip|gz|tar|mp3|mp4|avi|mov|jpg|jpeg|png|gif|svg|ico|css|js|woff|woff2|ttf|otf)$',
            re.IGNORECASE
        )

        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            full_url = full_url.split('#')[0].rstrip('/')

            parsed = urlparse(full_url)
            if parsed.netloc == base_parsed.netloc:
                if not ignore_ext.search(parsed.path):
                    internal_links.add(full_url)

        return list(internal_links)

    async def parse_sitemap(self, sitemap_url: str) -> List[str]:
        """Fetches and parses a sitemap.xml to extract URLs."""
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
                links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', content)

                expanded_urls = set()
                for link in links:
                    full_url = urljoin(url, link).split('#')[0].rstrip('/')
                    if full_url.startswith('http'):
                        expanded_urls.add(full_url)

                return list(expanded_urls)
        except Exception as e:
            logger.error(f"Failed to parse llms.txt {url}: {str(e)}")
            return []
