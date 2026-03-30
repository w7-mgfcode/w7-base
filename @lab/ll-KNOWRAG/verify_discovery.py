import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "apps/api/src"))

from server.services.crawling.discovery_service import DiscoveryService

async def test_discovery():
    service = DiscoveryService()
    test_urls = [
        "https://python.langchain.com",
        "https://docs.pydantic.dev",
        "google.com"
    ]
    
    for url in test_urls:
        print(f"\n--- Discovering: {url} ---")
        result = await service.discover(url)
        if result.success:
            print(f"Canonical URL: {result.canonical_url}")
            for target in result.targets:
                print(f"  [{target.priority}] {target.target_type.value}: {target.url}")
        else:
            print(f"Error: {result.error}")

if __name__ == "__main__":
    asyncio.run(test_discovery())
