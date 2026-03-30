import asyncio
import logging
import uuid
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import re

from server.services.crawling.discovery_service import DiscoveryService
from server.services.crawling.crawler_manager import CrawlerManager
from server.services.knowledge.ingestion_service import IngestionService
from server.models.crawling import CrawlRequest, CrawlProgress, CrawlStatus, CrawlMode, CrawlTask
from server.models.discovery import DiscoveryType

logger = logging.getLogger(__name__)

class CrawlingService:
    """
    Orchestrates the crawling process and feeds the ingestion layer.
    Ported from Archon: handles discovery, task generation, and execution.
    """
    
    def __init__(self, discovery_service: DiscoveryService, crawler_manager: CrawlerManager, ingestion_service: IngestionService):
        self.discovery_service = discovery_service
        self.crawler_manager = crawler_manager
        self.ingestion_service = ingestion_service
        # In a production environment, this would be a persistent store like Redis or DB
        self._active_crawls: Dict[str, CrawlProgress] = {}

    async def start_crawl(self, request: CrawlRequest) -> str:
        """
        Initiates a background crawl operation.
        """
        crawl_id = str(uuid.uuid4())
        progress = CrawlProgress(id=crawl_id, status=CrawlStatus.PENDING)
        self._active_crawls[crawl_id] = progress
        
        # Start the background task
        asyncio.create_task(self._run_crawl(crawl_id, request))
        
        return crawl_id

    def get_progress(self, crawl_id: str) -> Optional[CrawlProgress]:
        """
        Returns the current progress of a crawl operation.
        """
        return self._active_crawls.get(crawl_id)

    def stop_crawl(self, crawl_id: str) -> bool:
        """
        Cancels a crawl operation if it is pending or running.
        """
        progress = self._active_crawls.get(crawl_id)
        if not progress or progress.status not in (CrawlStatus.PENDING, CrawlStatus.RUNNING):
            return False
        progress.status = CrawlStatus.CANCELLED
        return True

    def _derive_source_id(self, base_url: str) -> str:
        """
        Derives a source_id slug from the base_url if not provided.
        """
        parsed = urlparse(base_url)
        netloc = parsed.netloc or parsed.path
        # Remove common prefixes and suffixes
        slug = netloc.replace("www.", "").split(".")[0]
        if not slug:
            return str(uuid.uuid4())[:8]
        return slug

    async def _run_crawl(self, crawl_id: str, request: CrawlRequest):
        """
        Internal crawl execution loop.
        """
        progress = self._active_crawls[crawl_id]
        progress.status = CrawlStatus.RUNNING
        
        source_id = request.source_id or self._derive_source_id(request.base_url)
        
        try:
            # 1. Discovery
            logger.info(f"Starting discovery for {request.base_url} (source_id: {source_id}, mode: {request.mode})")
            discovery_result = await self.discovery_service.discover(request.base_url)
            
            if not discovery_result.success:
                progress.status = CrawlStatus.FAILED
                progress.error = discovery_result.error
                return

            # 2. Planning (Task generation)
            tasks_queue = [] # Queue for recursive: List[(url, depth, type)]
            all_crawl_results = []
            visited_urls = set()
            
            # Helper to add task if not visited and within limits
            def add_to_queue(url, depth, t_type):
                url = url.split('#')[0].rstrip('/')
                if url not in visited_urls and len(visited_urls) < request.max_pages:
                    tasks_queue.append((url, depth, t_type))
                    visited_urls.add(url)
                    return True
                return False

            if request.mode == CrawlMode.SINGLE_PAGE:
                add_to_queue(discovery_result.canonical_url, 0, DiscoveryType.SINGLE_PAGE)
                
            elif request.mode == CrawlMode.SITEMAP:
                sitemap_urls = await self.crawler_manager.parse_sitemap(request.base_url)
                for url in sitemap_urls:
                    if not add_to_queue(url, 0, DiscoveryType.SINGLE_PAGE):
                        break # Respect max_pages
                        
            elif request.mode == CrawlMode.RECURSIVE:
                add_to_queue(discovery_result.canonical_url, 0, DiscoveryType.SINGLE_PAGE)
                
            elif request.mode == CrawlMode.DISCOVERY_AUTO:
                # Prioritize llms-full.txt, then llms.txt, then sitemap, then single page
                best_target = None
                for target in discovery_result.targets:
                    if target.target_type in (DiscoveryType.LLMS_FULL_TXT, DiscoveryType.LLMS_TXT):
                        best_target = target
                        break
                
                if not best_target:
                    # Fallback to sitemap or single page
                    for target in discovery_result.targets:
                        if target.target_type == DiscoveryType.SITEMAP_XML:
                            best_target = target
                            break
                
                if not best_target:
                    best_target = discovery_result.targets[-1] # Base URL

                if best_target.target_type == DiscoveryType.SITEMAP_XML:
                    sitemap_urls = await self.crawler_manager.parse_sitemap(best_target.url)
                    for url in sitemap_urls:
                        if not add_to_queue(url, 0, DiscoveryType.SINGLE_PAGE):
                            break
                elif best_target.target_type == DiscoveryType.LLMS_TXT:
                    # Expand llms.txt into multiple tasks
                    llms_urls = await self.crawler_manager.parse_llms_txt(best_target.url)
                    if llms_urls:
                        for url in llms_urls:
                            if not add_to_queue(url, 0, DiscoveryType.SINGLE_PAGE):
                                break
                    else:
                        # Fallback to fetching the llms.txt itself if no URLs extracted
                        add_to_queue(best_target.url, 0, best_target.target_type)
                else:
                    add_to_queue(best_target.url, 0, best_target.target_type)
            
            # 3. Execution loop (Breadth-first for recursive)
            progress.total_tasks = len(tasks_queue)
            
            q_idx = 0
            while q_idx < len(tasks_queue):
                if progress.status == CrawlStatus.CANCELLED:
                    logger.info(f"Crawl {crawl_id} cancelled.")
                    break
                    
                url, depth, t_type = tasks_queue[q_idx]
                q_idx += 1
                
                progress.current_task_url = url
                result = await self.crawler_manager.crawl(url)
                
                if result.get("success"):
                    # Special handling for llms-full.txt (split into pages)
                    if t_type == DiscoveryType.LLMS_FULL_TXT:
                        split_results = self._split_llms_full_txt(result)
                        all_crawl_results.extend(split_results)
                    else:
                        all_crawl_results.append(result)
                    
                    # If recursive mode, extract links from this page and add to queue
                    if request.mode == CrawlMode.RECURSIVE and depth < request.max_depth:
                        links = self.crawler_manager.extract_links(result.get("raw_html", ""), url)
                        for link in links:
                            add_to_queue(link, depth + 1, DiscoveryType.SINGLE_PAGE)
                        
                        # Update total tasks for progress reporting
                        progress.total_tasks = len(tasks_queue)
                    
                    progress.completed_tasks += 1
                else:
                    progress.failed_tasks += 1
                
                # Small delay to prevent rate limiting
                await asyncio.sleep(0.5)

            # 4. Trigger Ingestion (Authoritative Upstream)
            if all_crawl_results:
                logger.info(f"Triggering ingestion for {len(all_crawl_results)} results (source_id: {source_id})")
                
                # Merge request metadata with crawl-specific metadata
                ingestion_metadata = dict(request.metadata or {})
                ingestion_metadata["base_url"] = request.base_url
                
                await self.ingestion_service.ingest_crawl_results(
                    source_id=source_id,
                    crawl_results=all_crawl_results,
                    metadata=ingestion_metadata
                )

            progress.status = CrawlStatus.COMPLETED if progress.status != CrawlStatus.CANCELLED else CrawlStatus.CANCELLED
            progress.current_task_url = None
            
        except Exception as e:
            logger.exception(f"Crawl process {crawl_id} failed: {str(e)}")
            progress.status = CrawlStatus.FAILED
            progress.error = str(e)

    def _split_llms_full_txt(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Splits llms-full.txt content into multiple page results based on H1/H2 headers.
        """
        content = result.get("content", "")
        # Very simple split on H1 or H2
        sections = re.split(r'\n#+\s+', "\n" + content)
        pages = []
        section_idx = 0
        for section in sections:
            section = section.strip()
            if not section:
                continue

            lines = section.split("\n")
            title = lines[0] if lines else f"Section {section_idx}"

            pages.append({
                "url": f"{result.get('url')}#section-{section_idx}",
                "content": section,
                "title": title,
                "success": True,
                "metadata": {"section_index": section_idx}
            })
            section_idx += 1
        return pages
