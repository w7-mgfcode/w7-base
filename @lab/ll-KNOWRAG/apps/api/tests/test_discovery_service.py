import socket

import pytest

from server.services.crawling.discovery_service import DiscoveryService


def test_normalize_url_adds_https_and_strips_fragment(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))],
    )
    service = DiscoveryService()

    assert service.normalize_url("example.com/docs/#section") == "https://example.com/docs"


def test_normalize_url_rejects_invalid_scheme():
    service = DiscoveryService()

    with pytest.raises(ValueError, match="Invalid URL scheme"):
        service.normalize_url("ftp://example.com/resource")


def test_normalize_url_blocks_loopback_address():
    service = DiscoveryService()

    with pytest.raises(ValueError, match="Refusing to crawl private or local address"):
        service.normalize_url("http://127.0.0.1")


def test_normalize_url_blocks_private_address():
    service = DiscoveryService()

    with pytest.raises(ValueError, match="Refusing to crawl private or local address"):
        service.normalize_url("http://10.0.0.1")
