from server.models.discovery import DiscoveryType
from server.services.crawling.crawling_service import CrawlingService


def test_split_llms_full_txt_splits_sections_by_headers():
    service = CrawlingService(discovery_service=None, crawler_manager=None, ingestion_service=None)
    result = {
        "url": "https://example.com/llms-full.txt",
        "content": "# Intro\nIntro body\n## Usage\nUsage body",
    }

    pages = service._split_llms_full_txt(result)

    assert len(pages) == 2
    assert pages[0]["title"] == "Intro"
    assert pages[1]["title"] == "Usage"
    assert pages[0]["url"].endswith("#section-0")
    assert pages[1]["metadata"]["section_index"] == 1


def test_split_llms_full_txt_skips_empty_sections():
    service = CrawlingService(discovery_service=None, crawler_manager=None, ingestion_service=None)
    result = {
        "url": "https://example.com/llms-full.txt",
        "content": "\n\n# Intro\nOne\n\n## Details\nTwo",
    }

    pages = service._split_llms_full_txt(result)

    assert [page["title"] for page in pages] == ["Intro", "Details"]
    assert all(page["success"] is True for page in pages)
