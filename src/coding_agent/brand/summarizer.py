"""Summarize raw signals into actionable brand reports."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from coding_agent.brand.models import BrandReport, BrandSignal


@dataclass
class HeuristicSummarizer:
    """Simple rule-based summarizer suitable for MVP/testing."""

    def summarize(self, brand_id: str, report_date, signals: Iterable[BrandSignal]) -> BrandReport:
        unique_signals: list[BrandSignal] = []
        seen = set()
        for signal in signals:
            normalized_headline = " ".join(signal.headline.split())
            normalized_summary = " ".join(signal.summary.split()) if signal.summary else None
            key = (normalized_headline.lower(), normalized_summary.lower() if normalized_summary else None)
            if normalized_headline and key not in seen:
                seen.add(key)
                unique_signals.append(
                    BrandSignal(
                        source=signal.source,
                        headline=normalized_headline,
                        impact=signal.impact,
                        url=signal.url,
                        summary=normalized_summary,
                    )
                )

        signals_tuple = tuple(unique_signals)
        if not signals_tuple:
            fallback = BrandSignal(
                source="internal",
                headline="No external signals available",
                impact="low",
                summary="The automated collector did not find new items within the sampling window.",
            )
            signals_tuple = (fallback,)

        impact_counts = Counter(signal.impact for signal in signals_tuple)
        total = len(signals_tuple)
        share_high = round(impact_counts.get("high", 0) / total, 2) if total else 0.0
        share_medium = round(impact_counts.get("medium", 0) / total, 2) if total else 0.0
        unique_sources = len({signal.source for signal in signals_tuple})

        top_signal = next((s for s in signals_tuple if s.impact == "high"), signals_tuple[0])

        overview_parts: list[str] = []
        overview_parts.append(
            f"Key highlight: {top_signal.headline}."
        )
        overview_parts.append(
            f"Signal mix includes {impact_counts.get('high', 0)} high-impact and {impact_counts.get('medium', 0)} medium-impact items across {unique_sources} sources."
        )
        overview = " ".join(overview_parts)

        actions: list[str] = []
        for signal in signals_tuple:
            if signal.impact == "high":
                actions.append(f"Investigate: {signal.headline}")
            elif signal.impact == "medium":
                actions.append(f"Monitor: {signal.headline}")
        if not actions:
            actions.append("Monitor brand sentiment for additional changes.")
        if len(actions) == 1:
            actions.append("Review competitor activity for emerging campaigns.")

        risks: list[str] = []
        if impact_counts.get("high", 0) == 0:
            risks.append("No high-impact external signals detected; consider manual scan to confirm stability.")
        if total < 3:
            risks.append("Limited signal volume; treat conclusions as directional.")

        metrics = {
            "total_signals": total,
            "high_signals": impact_counts.get("high", 0),
            "medium_signals": impact_counts.get("medium", 0),
            "low_signals": impact_counts.get("low", 0),
            "high_signal_ratio": share_high,
            "medium_signal_ratio": share_medium,
            "unique_sources": unique_sources,
        }

        return BrandReport(
            brand_id=brand_id,
            report_date=report_date,
            highlights=signals_tuple,
            metrics=metrics,
            actions=tuple(actions[:4]),
            overview=overview,
            risks=tuple(risks),
        )
