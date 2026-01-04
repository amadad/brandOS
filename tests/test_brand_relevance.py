from datetime import date

from coding_agent.brand.config import BrandProfile
from coding_agent.brand.models import BrandSignal
from coding_agent.brand.relevance import apply_relevance_filter


def make_profile() -> BrandProfile:
    return BrandProfile(
        brand_id="givecare",
        company_summary="GiveCare remote patient monitoring",
        keywords=["givecare", "remote"],
        competitors=["care.com"],
        stop_phrases=["bosch"],
    )


def test_relevance_accepts_keyword_match():
    signals = (
        BrandSignal(source="news", headline="GiveCare launches RPM dashboard", impact="high", summary="Remote monitoring"),
    )

    filtered, rejected = apply_relevance_filter(signals, make_profile())

    assert len(filtered) == 1
    assert not rejected
    assert "Relevance" in filtered[0].summary


def test_relevance_rejects_stop_phrase():
    signals = (
        BrandSignal(source="news", headline="Bosch electronics sale", impact="low", summary="Give care instructions"),
    )

    filtered, rejected = apply_relevance_filter(signals, make_profile())

    assert not filtered
    assert rejected[0].reason.startswith("stop phrase")


def test_relevance_requires_keyword():
    signals = (
        BrandSignal(source="news", headline="Generic wellness article", impact="low", summary="Tips for caregivers"),
    )

    filtered, rejected = apply_relevance_filter(signals, make_profile())

    assert not filtered
    assert rejected[0].reason == "no matching brand keywords"
