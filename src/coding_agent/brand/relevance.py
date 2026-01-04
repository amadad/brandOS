"""Relevance filtering for brand signals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from coding_agent.brand.config import BrandProfile
from coding_agent.brand.models import BrandSignal


@dataclass(frozen=True)
class RejectedSignal:
    signal: BrandSignal
    reason: str


def apply_relevance_filter(
    signals: Sequence[BrandSignal],
    profile: BrandProfile,
    *,
    min_keyword_hits: int = 1,
) -> Tuple[Tuple[BrandSignal, ...], Tuple[RejectedSignal, ...]]:
    """Filter signals using brand keywords, competitor mentions, and stop phrases."""

    keywords = profile.keyword_set()
    competitor_terms = profile.competitor_set()
    stop_terms = profile.stop_phrase_set()

    accepted: List[BrandSignal] = []
    rejected: List[RejectedSignal] = []

    for signal in signals:
        text = f"{signal.headline} {signal.summary or ''}".lower()
        stop_matches = {term for term in stop_terms if term and term in text}
        if stop_matches:
            rejected.append(
                RejectedSignal(signal=signal, reason=f"stop phrase(s) {sorted(stop_matches)}")
            )
            continue

        keyword_hits = {term for term in keywords if term and term in text}
        competitor_hits = {term for term in competitor_terms if term and term in text}

        if len(keyword_hits) < min_keyword_hits and not competitor_hits:
            rejected.append(
                RejectedSignal(signal=signal, reason="no matching brand keywords")
            )
            continue

        relevance_clauses: List[str] = []
        if keyword_hits:
            relevance_clauses.append("keywords " + ", ".join(sorted(keyword_hits)))
        if competitor_hits:
            relevance_clauses.append("competitors " + ", ".join(sorted(competitor_hits)))

        addendum = " (Relevance: " + "; ".join(relevance_clauses) + ")"
        existing_summary = signal.summary or ""
        new_summary = (existing_summary + addendum).strip() if existing_summary else addendum.strip()
        accepted.append(signal.model_copy(update={"summary": new_summary}))

    return tuple(accepted), tuple(rejected)


__all__ = ["apply_relevance_filter", "RejectedSignal"]
