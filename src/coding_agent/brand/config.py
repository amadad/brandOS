"""Brand profile loading helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "brand_profiles.yaml"


@dataclass(frozen=True)
class BrandProfile:
    brand_id: str
    company_summary: str
    keywords: List[str] = field(default_factory=list)
    competitors: List[str] = field(default_factory=list)
    stop_phrases: List[str] = field(default_factory=list)

    def keyword_set(self) -> set[str]:
        return {kw.lower() for kw in self.keywords if kw}

    def competitor_set(self) -> set[str]:
        return {kw.lower() for kw in self.competitors if kw}

    def stop_phrase_set(self) -> set[str]:
        return {kw.lower() for kw in self.stop_phrases if kw}


@lru_cache(maxsize=1)
def _raw_profiles(path: Path | None = None) -> Dict[str, dict]:
    config_path = path or CONFIG_PATH
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    return loaded


def get_brand_profile(brand_id: str, *, path: Path | None = None) -> BrandProfile:
    brand_id_normalized = brand_id.lower()
    raw = _raw_profiles(path).get(brand_id_normalized)
    if raw is None:
        return BrandProfile(
            brand_id=brand_id_normalized,
            company_summary=f"Monitoring updates for {brand_id_normalized}.",
            keywords=[brand_id_normalized.replace("_", " ")],
        )

    return BrandProfile(
        brand_id=brand_id_normalized,
        company_summary=raw.get("company_summary", f"Monitoring updates for {brand_id_normalized}."),
        keywords=raw.get("keywords", []) or [],
        competitors=raw.get("competitors", []) or [],
        stop_phrases=raw.get("stop_phrases", []) or [],
    )


__all__ = ["BrandProfile", "get_brand_profile"]
