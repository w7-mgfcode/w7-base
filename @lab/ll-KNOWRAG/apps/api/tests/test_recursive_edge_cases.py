import pytest
from unittest.mock import AsyncMock, MagicMock
from server.services.crawling.crawler_manager import CrawlerManager
from server.services.crawling.crawling_service import CrawlingService
from server.models.crawling import CrawlRequest, CrawlMode, CrawlProgress
from server.models.discovery import DiscoveryResult, DiscoveryTarget, DiscoveryType

@pytest.mark.asyncio
async def test_recursive_crawl_handles_different_content_types():
    mock_discovery = MagicMock()
    mock_discovery.discover = AsyncMock(return_value=DiscoveryResult(
        base_url="http://test.com", canonical_url="http://test.com",
        targets=[DiscoveryTarget(url="http://test.com", target_type=DiscoveryType.SINGLE_PAGE, priority=10)]
    ))
    
    mock_crawler = MagicMock()
    # Simulate a response that has links but content-type is NOT exactly text/html (e.g. text/html; charset=utf-8)
    async def mock_crawl(url):
        if url == "http://test.com":
            # The bug was that raw_html was only populated if parser=='html.parser'
            # which depended on 'xml' not being in content_type.
            return {
                "url": url, "success": True, 
                "raw_html": '<a href="/l1">L1</a>',
                "content": "Root"
            }
        return {"url": url, "success": True, "raw_html": '', "content": "Sub"}
        
    mock_crawler.crawl = AsyncMock(side_effect=mock_crawl)
    mock_crawler.extract_links = CrawlerManager().extract_links
    
    mock_ingestion = MagicMock()
    mock_ingestion.ingest_crawl_results = AsyncMock()
    
    service = CrawlingService(mock_discovery, mock_crawler, mock_ingestion)
    crawl_id = "test-content-type"
    service._active_crawls[crawl_id] = CrawlProgress(id=crawl_id)
    
    request = CrawlRequest(base_url="http://test.com", mode=CrawlMode.RECURSIVE, max_depth=1, max_pages=10)
    await service._run_crawl(crawl_id, request)
    
    # Should have fetched root + l1
    assert mock_crawler.crawl.call_count == 2

@pytest.mark.asyncio
async def test_recursive_crawl_handles_multiple_initial_tasks():
    # If discovery returns multiple targets (e.g. llms.txt + sitemap),
    # does recursion still work from them?
    mock_discovery = MagicMock()
    mock_discovery.discover = AsyncMock(return_value=DiscoveryResult(
        base_url="http://test.com", canonical_url="http://test.com",
        targets=[
            DiscoveryTarget(url="http://test.com/llms.txt", target_type=DiscoveryType.LLMS_TXT, priority=100),
            DiscoveryTarget(url="http://test.com/", target_type=DiscoveryType.SINGLE_PAGE, priority=10)
        ]
    ))
    
    mock_crawler = MagicMock()
    async def mock_crawl(url):
        if url == "http://test.com/":
            return {"url": url, "success": True, "raw_html": '<a href="/page1">P1</a>', "content": "Root"}
        return {"url": url, "success": True, "raw_html": '', "content": "Other"}
        
    mock_crawler.crawl = AsyncMock(side_effect=mock_crawl)
    mock_crawler.extract_links = CrawlerManager().extract_links
    # Mock parse_llms_txt to return nothing to force fallback/multiple targets
    mock_crawler.parse_llms_txt = AsyncMock(return_value=[])
    
    mock_ingestion = MagicMock()
    mock_ingestion.ingest_crawl_results = AsyncMock()
    
    service = CrawlingService(mock_discovery, mock_crawler, mock_ingestion)
    crawl_id = "test-multi-target"
    service._active_crawls[crawl_id] = CrawlProgress(id=crawl_id)
    
    # In DISCOVERY_AUTO, it picks the BEST target.
    # If LLMS_TXT is picked but yields no URLs, it falls back to fetching llms.txt itself.
    # The current logic doesn't continue to the next best target.
    
    request = CrawlRequest(base_url="http://test.com", mode=CrawlMode.RECURSIVE, max_depth=1, max_pages=10)
    await service._run_crawl(crawl_id, request)
    
    # In RECURSIVE mode, it now enqueues ALL discovered targets as roots.
    # Targets: llms.txt (1) + root (2)
    # Root has link to P1 (3)
    assert mock_crawler.crawl.call_count == 3
