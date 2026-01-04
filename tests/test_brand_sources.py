from pathlib import Path

from coding_agent.brand.models import BrandSignal
from unittest.mock import MagicMock, patch

from coding_agent.brand.sources import (
    FileSignalsProvider,
    StaticSignalsProvider,
    WebPageSignalsProvider,
    GoogleNewsProvider,
)


def test_file_signals_provider(tmp_path: Path):
    sample = tmp_path / "signals.json"
    sample.write_text(
        '[{"source": "news", "headline": "Test", "impact": "high"}]', encoding="utf-8"
    )

    provider = FileSignalsProvider(path=sample)
    signals = list(provider.load(brand_id="acme"))

    assert len(signals) == 1
    assert isinstance(signals[0], BrandSignal)
    assert signals[0].headline == "Test"


def test_static_signals_provider():
    signal = BrandSignal(source="news", headline="Static", impact="low")
    provider = StaticSignalsProvider([signal])

    signals = list(provider.load("brand"))
    assert signals == [signal]


@patch("coding_agent.brand.sources.requests.get")
def test_web_page_signals_provider(mock_get: MagicMock):
    mock_response = MagicMock()
    mock_response.text = """
        <html>
          <head><title>BrandOS Agency</title><meta name=\"description\" content=\"Creative agency for brands\"></head>
          <body>
            <h1>Latest Work</h1>
            <p>New campaign launched for X.</p>
          </body>
        </html>
    """
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    provider = WebPageSignalsProvider(url="https://example.com")
    signals = list(provider.load("brand"))

    assert len(signals) >= 1
    assert signals[0].headline == "BrandOS Agency"
    assert signals[0].summary == "Creative agency for brands"


@patch("coding_agent.brand.sources.requests.get")
def test_google_news_provider(mock_get: MagicMock):
    mock_response = MagicMock()
    mock_response.text = """
    <rss><channel>
      <item>
        <title>GiveCare partners with HealthCo</title>
        <link>https://news.example.com/article</link>
        <description>Remote care coverage expands.</description>
      </item>
    </channel></rss>
    """
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    provider = GoogleNewsProvider(query="givecare")
    signals = list(provider.load("givecare"))

    assert len(signals) == 1
    assert signals[0].headline.startswith("GiveCare")
    assert signals[0].url == "https://news.example.com/article"
