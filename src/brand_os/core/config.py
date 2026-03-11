"""Configuration loading and management."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    """Get current UTC time as timezone-aware datetime.

    Use this instead of datetime.utcnow() which is deprecated in Python 3.12+.
    """
    return datetime.now(UTC)


class BrandOpsConfig(BaseModel):
    """Global configuration for brandos."""

    brands_dir: Path = Field(default_factory=lambda: Path("brands"))
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".brandos")
    default_provider: str = "gemini"
    default_model: str | None = None


_config: BrandOpsConfig | None = None


def get_config() -> BrandOpsConfig:
    """Get the global configuration, loading from file if needed."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def load_config(path: Path | None = None) -> BrandOpsConfig:
    """Load configuration from YAML file."""
    if path is None:
        # Check environment variable first
        env_path = os.getenv("BRANDOPS_CONFIG")
        if env_path:
            path = Path(env_path)
        else:
            # Default locations
            for candidate in [
                Path.cwd() / "brandos.yml",
                Path.home() / ".brandos" / "config.yml",
            ]:
                if candidate.exists():
                    path = candidate
                    break

    if path and path.exists():
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return BrandOpsConfig(**data)

    return BrandOpsConfig()


def get_env(key: str, default: str | None = None) -> str | None:
    """Get environment variable with BRANDOPS_ prefix."""
    return os.getenv(f"BRANDOPS_{key.upper()}", default)


def get_api_key(provider: str) -> str | None:
    """Get API key for a provider."""
    key_map = {
        "gemini": "GOOGLE_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }
    env_var = key_map.get(provider, f"{provider.upper()}_API_KEY")
    return os.getenv(env_var)


def get_brands_dir() -> Path:
    """Get the brands directory."""
    config = get_config()
    brands_dir = config.brands_dir
    if not brands_dir.is_absolute():
        brands_dir = Path.cwd() / brands_dir
    return brands_dir


def load_brand_config(brand: str) -> dict[str, Any] | None:
    """Load configuration for a specific brand.

    Args:
        brand: Brand name/slug

    Returns:
        Brand configuration dict or None if not found
    """
    brands_dir = get_brands_dir()
    brand_file = brands_dir / brand / "brand.yml"

    if not brand_file.exists():
        return None

    with open(brand_file) as f:
        return yaml.safe_load(f) or {}


def list_brands() -> list[str]:
    """List all available brands."""
    brands_dir = get_brands_dir()
    if not brands_dir.exists():
        return []

    return [
        d.name
        for d in brands_dir.iterdir()
        if d.is_dir() and (d / "brand.yml").exists() and not d.name.startswith("_")
    ]
