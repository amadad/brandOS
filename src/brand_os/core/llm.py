from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol


class ProviderError(RuntimeError):
    pass


class LLMProvider(Protocol):
    def complete(self, prompt: str, system: str | None = None, model: str | None = None) -> str: ...

    def complete_json(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        default: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...


@dataclass
class LLMConfig:
    provider: str = "mock"
    model: str | None = None


class MockProvider:
    def complete(self, prompt: str, system: str | None = None, model: str | None = None) -> str:
        return ""

    def complete_json(
        self,
        prompt: str,
        system: str | None = None,
        model: str | None = None,
        default: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return default or {}


def get_provider(name: str | None = None) -> LLMProvider:
    provider = name or os.getenv("BRANDOPS_LLM_PROVIDER", "mock")
    if provider == "mock":
        return MockProvider()
    raise ProviderError(f"Unknown LLM provider: {provider}")


def complete(prompt: str, system: str | None = None, model: str | None = None) -> str:
    provider = get_provider()
    return provider.complete(prompt=prompt, system=system, model=model)


def complete_json(
    prompt: str,
    system: str | None = None,
    model: str | None = None,
    default: dict[str, Any] | None = None,
) -> dict[str, Any]:
    provider = get_provider()
    return provider.complete_json(prompt=prompt, system=system, model=model, default=default)
