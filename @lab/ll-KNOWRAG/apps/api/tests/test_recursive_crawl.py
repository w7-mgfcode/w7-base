import pytest
from unittest.mock import AsyncMock, MagicMock
from server.services.crawling.crawler_manager import CrawlerManager
from server.services.crawling.crawling_service import CrawlingService
from server.models.crawling import CrawlRequest, CrawlMode, CrawlProgress
from server.models.discovery import DiscoveryResult, DiscoveryTarget, DiscoveryType

def test_extract_links_filters_correctly():
    manager = CrawlerManager()
    html = """
        <a href="/page1">Internal</a>
        <a href="https://other.com/page2">External</a>
        <a href="/image.jpg">Image</a>
        <a href="/docs#section">Fragment</a>
    """
    links = manager.extract_links(html, "https://example.com")
    
    assert "https://example.com/page1" in links
    assert "https://example.com/docs" in links
    assert "https://other.com/page2" not in links
    assert "https://example.com/image.jpg" not in links
    assert len(links) == 2

@pytest.mark.asyncio
async def test_recursive_crawl_stops_at_depth():
    mock_discovery = MagicMock()
    mock_discovery.discover = AsyncMock(return_value=DiscoveryResult(
        base_url="http://test.com", canonical_url="http://test.com",
        targets=[DiscoveryTarget(url="http://test.com", target_type=DiscoveryType.SINGLE_PAGE, priority=10)]
    ))
    
    mock_crawler = MagicMock()
    # Level 0 (root) has links to Level 1
    # Level 1 has links to Level 2
    async def mock_crawl(url):
        if url == "http://test.com":
            return {"url": url, "success": True, "raw_html": '<a href="/l1">L1</a>'}
        if url == "http://test.com/l1":
            return {"url": url, "success": True, "raw_html": '<a href="/l2">L2</a>'}
        return {"url": url, "success": True, "raw_html": ''}
        
    mock_crawler.crawl = AsyncMock(side_effect=mock_crawl)
    mock_crawler.extract_links = CrawlerManager().extract_links
    
    mock_ingestion = MagicMock()
    mock_ingestion.ingest_crawl_results = AsyncMock()
    
    service = CrawlingService(mock_discovery, mock_crawler, mock_ingestion)
    crawl_id = "test-rec"
    service._active_crawls[crawl_id] = CrawlProgress(id=crawl_id)
    
    # Depth 1: Should only get root and l1
    request = CrawlRequest(base_url="http://test.com", mode=CrawlMode.RECURSIVE, max_depth=1, max_pages=10)
    await service._run_crawl(crawl_id, request)
    
    args, kwargs = mock_ingestion.ingest_crawl_results.call_args
    results = kwargs.get("crawl_results") or args[1]
    urls = [r["url"] for r in results]
    
    assert "http://test.com" in urls
    assert "http://test.com/l1" in urls
    assert "http://test.com/l2" not in urls
    assert len(urls) == 2

@pytest.mark.asyncio
async def test_recursive_crawl_stops_at_max_pages():
    mock_discovery = MagicMock()
    mock_discovery.discover = AsyncMock(return_value=DiscoveryResult(
        base_url="http://test.com", canonical_url="http://test.com",
        targets=[DiscoveryTarget(url="http://test.com", target_type=DiscoveryType.SINGLE_PAGE, priority=10)]
    ))
    
    mock_crawler = MagicMock()
    async def mock_crawl(url):
        return {"url": url, "success": True, "raw_html": '<a href="/1">1</a><a href="/2">2</a><a href="/3">3</a>'}
        
    mock_crawler.crawl = AsyncMock(side_effect=mock_crawl)
    mock_crawler.extract_links = CrawlerManager().extract_links
    
    mock_ingestion = MagicMock()
    mock_ingestion.ingest_crawl_results = AsyncMock()
    
    service = CrawlingService(mock_discovery, mock_crawler, mock_ingestion)
    crawl_id = "test-pages"
    service._active_crawls[crawl_id] = CrawlProgress(id=crawl_id)
    
    # Max pages 2: Should only get root and one link
    request = CrawlRequest(base_url="http://test.com", mode=CrawlMode.RECURSIVE, max_depth=5, max_pages=2)
    await service._run_crawl(crawl_id, request)
    
    args, kwargs = mock_ingestion.ingest_crawl_results.call_args
    results = kwargs.get("crawl_results") or args[1]
    assert len(results) == 2
