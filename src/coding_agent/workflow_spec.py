"""Pure-Python specifications for the Temporal workflow wiring."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Tuple


@dataclass(frozen=True)
class RetryPolicy:
    """The minimal retry policy we expect Activities to honor."""

    maximum_attempts: int = 3
    initial_interval: timedelta = timedelta(seconds=10)


@dataclass(frozen=True)
class WorkflowActivity:
    """Describes a Temporal Activity invoked by the workflow."""

    name: str
    timeout: timedelta = timedelta(minutes=5)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)


@dataclass(frozen=True)
class WorkflowSignal:
    """Describes a Temporal Signal the workflow will listen for."""

    name: str
    description: str


@dataclass(frozen=True)
class CodingTaskWorkflowSpec:
    """Named collection of Activities, Signals, and timeouts."""

    name: str
    activities: Tuple[WorkflowActivity, ...]
    signals: Tuple[WorkflowSignal, ...]
    sleep_timeout: timedelta

    @classmethod
    def default(cls) -> "CodingTaskWorkflowSpec":
        activities = (
            WorkflowActivity("PlanChanges", timeout=timedelta(minutes=3)),
            WorkflowActivity("FetchContext", timeout=timedelta(minutes=2)),
            WorkflowActivity("ApplyDiffs", timeout=timedelta(minutes=10)),
            WorkflowActivity("RunCI", timeout=timedelta(minutes=30)),
            WorkflowActivity("OpenPR", timeout=timedelta(minutes=5)),
            WorkflowActivity("AwaitReview", timeout=timedelta(days=2)),
            WorkflowActivity("AddressFeedback", timeout=timedelta(minutes=15)),
        )

        signals = (
            WorkflowSignal(
                name="review",
                description=(
                    "Signal emitted when a reviewer responds; resumes the workflow"
                ),
            ),
        )

        return cls(
            name="CodingTaskWorkflow",
            activities=activities,
            signals=signals,
            sleep_timeout=timedelta(hours=12),
        )
