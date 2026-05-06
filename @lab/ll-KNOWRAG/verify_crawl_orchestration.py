import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "apps/api/src"))

from server.services.crawling.discovery_service import DiscoveryService
from server.services.crawling.crawler_manager import CrawlerManager
from server.services.crawling.crawling_service import CrawlingService
from server.models.crawling import CrawlRequest, CrawlMode

async def test_crawl_orchestration():
    discovery = DiscoveryService()
    manager = CrawlerManager()
    service = CrawlingService(discovery, manager)
    
    request = CrawlRequest(
        base_url="https://python.langchain.com",
        mode=CrawlMode.DISCOVERY_AUTO
    )
    
    print(f"\n--- Testing Crawl Orchestration: {request.base_url} ---")
    crawl_id = await service.start_crawl(request)
    print(f"Started crawl with ID: {crawl_id}")
    
    # Poll for progress
    for _ in range(10):
        progress = service.get_progress(crawl_id)
        if progress:
            print(f"Status: {progress.status.value} | Tasks: {progress.completed_tasks}/{progress.total_tasks}")
            if progress.status in ("completed", "failed"):
                if progress.error:
                    print(f"Error: {progress.error}")
                break
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(test_crawl_orchestration())
