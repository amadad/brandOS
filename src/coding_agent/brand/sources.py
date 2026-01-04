"""Signal providers for brand reporting."""

from __future__ import annotations

import ipaddress
import json
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET

from coding_agent.brand.models import BrandSignal


def _validate_url(url: str) -> None:
    """Validate URL to prevent SSRF attacks."""
    parsed = urlparse(url)

    # Only allow http/https schemes
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"URL scheme must be http or https, got: {parsed.scheme}")

    if not parsed.netloc:
        raise ValueError("URL must have a valid host")

    # Extract hostname (remove port if present)
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL must have a valid hostname")

    # Block localhost and common internal hostnames
    blocked_hosts = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "[::1]"}
    if hostname.lower() in blocked_hosts:
        raise ValueError("URL points to localhost (blocked)")

    # Resolve hostname and check for private IP ranges
    try:
        resolved_ips = socket.getaddrinfo(hostname, None)
        for family, type_, proto, canonname, sockaddr in resolved_ips:
            ip_str = sockaddr[0]
            ip = ipaddress.ip_address(ip_str)
            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                raise ValueError(f"URL resolves to private/internal IP: {ip_str}")
    except socket.gaierror:
        # If DNS resolution fails, allow the request to proceed
        # (will fail naturally on the HTTP request)
        pass


class SignalsProvider(Protocol):
    """Protocol for loading brand signals from a source."""

    def load(self, brand_id: str) -> Iterable[BrandSignal]: ...


@dataclass
class FileSignalsProvider:
    """Loads signals from a JSON file on disk."""

    path: Path

    def load(self, brand_id: str) -> Iterable[BrandSignal]:
        with self.path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        for raw in data:
            yield BrandSignal.model_validate(raw)


class StaticSignalsProvider(SignalsProvider):
    """Provides a pre-defined set of signals (useful for tests)."""

    def __init__(self, signals: Iterable[BrandSignal]):
        self._signals = tuple(signals)

    def load(self, brand_id: str) -> Iterable[BrandSignal]:
        return self._signals


@dataclass
class WebPageSignalsProvider(SignalsProvider):
    """Fetches a public web page and extracts simple highlight signals."""

    url: str
    timeout: float = 8.0

    def load(self, brand_id: str) -> Iterable[BrandSignal]:
        _validate_url(self.url)
        response = requests.get(self.url, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        signals: list[BrandSignal] = []

        title = (soup.title.string if soup.title else "").strip()
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = (description_tag["content"].strip() if description_tag and description_tag.get("content") else "")

        if title:
            signals.append(
                BrandSignal(
                    source="web",
                    headline=title,
                    impact="medium",
                    url=self.url,
                    summary=description or None,
                )
            )

        headings = soup.find_all(["h1", "h2", "h3"], limit=5)
        for heading in headings:
            text = heading.get_text(strip=True)
            if not text or any(sig.headline == text for sig in signals):
                continue
            summary = None
            paragraph = heading.find_next("p")
            if paragraph:
                summary = paragraph.get_text(strip=True)[:280] or None
            signals.append(
                BrandSignal(
                    source="web",
                    headline=text,
                    impact="low",
                    url=self.url,
                    summary=summary,
                )
            )

        if not signals:
            signals.append(
                BrandSignal(
                    source="web",
                    headline=f"Update from {self.url}",
                    impact="low",
                    url=self.url,
                    summary="No readable content extracted; manual review recommended.",
                )
            )

        return signals


@dataclass
class GoogleNewsProvider(SignalsProvider):
    """Pulls recent items from Google News RSS for a query."""

    query: str
    max_items: int = 5
    timeout: float = 8.0

    def load(self, brand_id: str) -> Iterable[BrandSignal]:
        encoded_query = requests.utils.quote(self.query)
        url = (
            "https://news.google.com/rss/search?q="
            f"{encoded_query}&hl=en-US&gl=US&ceid=US:en"
        )

        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        channel = root.find("channel")
        if channel is None:
            return []

        items = channel.findall("item")[: self.max_items]
        signals: list[BrandSignal] = []
        for item in items:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            description = (item.findtext("description") or "").strip()
            if not title:
                continue
            parsed_host = ""
            if link:
                parsed_host = requests.utils.urlparse(link).netloc
            source_label = parsed_host or "google-news"
            signals.append(
                BrandSignal(
                    source=source_label,
                    headline=title,
                    impact="medium",
                    url=link or None,
                    summary=description or None,
                )
            )
        return signals
