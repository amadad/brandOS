"""Thin orchestration skeleton mapping to Temporal Activities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from coding_agent.models import ChangePlan


@dataclass(frozen=True)
class TaskInput:
    """Input parameters for a workflow run."""

    ticket_id: str
    repository: str
    base_branch: str


@dataclass(frozen=True)
class CIResult:
    """Outcome of running CI for a proposed change."""

    passed: bool
    url: Optional[str] = None
    details: Optional[str] = None


@dataclass(frozen=True)
class ReviewResult:
    """Represents reviewer state after a PR is opened."""

    approved: bool
    feedback: Optional[str] = None


class CodingTaskOrchestrator:
    """Coordinates high-level Activities while deferring side effects to callables."""

    def __init__(
        self,
        *,
        plan_changes: Callable[[TaskInput], ChangePlan],
        fetch_context: Callable[[TaskInput, ChangePlan], Any],
        apply_diffs: Callable[[TaskInput, ChangePlan, Any], str],
        run_ci: Callable[[TaskInput, ChangePlan, str], CIResult],
        open_pr: Callable[[TaskInput, ChangePlan, str, CIResult], str],
        await_review: Callable[[TaskInput, str], ReviewResult],
        address_feedback: Optional[Callable[[TaskInput, str, ReviewResult], ReviewResult]] = None,
    ) -> None:
        self._plan_changes = plan_changes
        self._fetch_context = fetch_context
        self._apply_diffs = apply_diffs
        self._run_ci = run_ci
        self._open_pr = open_pr
        self._await_review = await_review
        self._address_feedback = address_feedback

    def run(self, task: TaskInput) -> str:
        plan = self._plan_changes(task)
        self._validate_plan(plan)

        context = self._fetch_context(task, plan)
        commit_sha = self._apply_diffs(task, plan, context)

        ci_result = self._run_ci(task, plan, commit_sha)
        if not ci_result.passed:
            raise RuntimeError("CI failed; aborting before PR creation")

        pr_url = self._open_pr(task, plan, commit_sha, ci_result)
        review_result = self._await_review(task, pr_url)

        if not review_result.approved:
            if self._address_feedback is None:
                raise RuntimeError("Review requested changes and no feedback handler was configured")
            updated_review = self._address_feedback(task, pr_url, review_result)
            if not isinstance(updated_review, ReviewResult):
                raise RuntimeError("address_feedback must return a ReviewResult")
            if not updated_review.approved:
                raise RuntimeError("Changes requested remain unresolved")

        return pr_url

    @staticmethod
    def _validate_plan(plan: ChangePlan) -> None:
        if plan.edits and not any("test" in check.lower() for check in plan.checks):
            raise ValueError("Plans with edits must include a test-related check")
