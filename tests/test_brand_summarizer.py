from datetime import date

from coding_agent.brand.models import BrandSignal
from coding_agent.brand.summarizer import HeuristicSummarizer


def test_heuristic_summarizer_generates_metrics():
    signals = (
        BrandSignal(source="news", headline="Major launch", impact="high"),
        BrandSignal(source="social", headline="Buzz", impact="medium"),
    )

    summarizer = HeuristicSummarizer()
    report = summarizer.summarize("brand", date(2025, 1, 15), signals)

    assert report.metrics["total_signals"] == 2
    assert report.metrics["high_signal_ratio"] == 0.5
    assert report.overview is not None
    assert report.actions[0].startswith("Investigate")
    assert len(report.actions) >= 2
