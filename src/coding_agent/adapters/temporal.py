"""Temporal-facing utilities for awaiting human review signals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from coding_agent.orchestrator import ReviewResult, TaskInput


class ReviewSignalGateway(Protocol):
    """Abstracts Temporal signal handling for review events."""

    def wait_for_review(self, task: TaskInput, pr_url: str) -> ReviewResult: ...


@dataclass
class TemporalAwaiter:
    """Delegates review waits to an injected Temporal gateway."""

    gateway: ReviewSignalGateway

    def await_review(self, task: TaskInput, pr_url: str) -> ReviewResult:
        return self.gateway.wait_for_review(task, pr_url)
