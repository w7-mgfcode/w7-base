import pytest
from unittest.mock import AsyncMock, MagicMock
from server.services.crawling.crawler_manager import CrawlerManager
from server.services.crawling.crawling_service import CrawlingService
from server.models.crawling import CrawlRequest, CrawlMode, CrawlProgress
from server.models.discovery import DiscoveryResult, DiscoveryTarget, DiscoveryType

@pytest.mark.asyncio
async def test_llmstxt_expansion_creates_tasks():
    mock_discovery = MagicMock()
    mock_discovery.discover = AsyncMock(return_value=DiscoveryResult(
        base_url="http://test.com", canonical_url="http://test.com",
        targets=[DiscoveryTarget(url="http://test.com/llms.txt", target_type=DiscoveryType.LLMS_TXT, priority=100)]
    ))
    
    mock_crawler = MagicMock()
    # Mock llms.txt content
    async def mock_parse_llms(url):
        return ["http://test.com/page1", "http://test.com/page2"]
    mock_crawler.parse_llms_txt = AsyncMock(side_effect=mock_parse_llms)
    mock_crawler.crawl = AsyncMock(return_value={"url": "any", "success": True})
    
    mock_ingestion = MagicMock()
    mock_ingestion.ingest_crawl_results = AsyncMock()
    
    service = CrawlingService(mock_discovery, mock_crawler, mock_ingestion)
    crawl_id = "test-llms"
    service._active_crawls[crawl_id] = CrawlProgress(id=crawl_id)
    
    request = CrawlRequest(base_url="http://test.com", mode=CrawlMode.DISCOVERY_AUTO, max_pages=10)
    await service._run_crawl(crawl_id, request)
    
    # Should have called crawl for page1 and page2
    assert mock_crawler.crawl.call_count == 2
    
    args, kwargs = mock_ingestion.ingest_crawl_results.call_args
    results = kwargs.get("crawl_results") or args[1]
    assert len(results) == 2

@pytest.mark.asyncio
async def test_llmstxt_expansion_respects_max_pages():
    mock_discovery = MagicMock()
    mock_discovery.discover = AsyncMock(return_value=DiscoveryResult(
        base_url="http://test.com", canonical_url="http://test.com",
        targets=[DiscoveryTarget(url="http://test.com/llms.txt", target_type=DiscoveryType.LLMS_TXT, priority=100)]
    ))
    
    mock_crawler = MagicMock()
    async def mock_parse_llms(url):
        return ["http://test.com/1", "http://test.com/2", "http://test.com/3"]
    mock_crawler.parse_llms_txt = AsyncMock(side_effect=mock_parse_llms)
    mock_crawler.crawl = AsyncMock(return_value={"url": "any", "success": True})
    
    mock_ingestion = MagicMock()
    mock_ingestion.ingest_crawl_results = AsyncMock()
    
    service = CrawlingService(mock_discovery, mock_crawler, mock_ingestion)
    crawl_id = "test-llms-limit"
    service._active_crawls[crawl_id] = CrawlProgress(id=crawl_id)
    
    request = CrawlRequest(base_url="http://test.com", mode=CrawlMode.DISCOVERY_AUTO, max_pages=2)
    await service._run_crawl(crawl_id, request)
    
    # Only 2 pages allowed
    assert mock_crawler.crawl.call_count == 2
