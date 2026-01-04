"""Agent-facing adapters that produce toolkit callables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from coding_agent.models import ChangePlan
from coding_agent.orchestrator import CIResult, ReviewResult, TaskInput
from coding_agent.runtime import AgentsToolkit


@dataclass
class PlannerAgentAdapter:
    """Adapter around a planner agent callable."""

    run_plan: Callable[[TaskInput], ChangePlan]

    def plan(self, task: TaskInput) -> ChangePlan:
        return self.run_plan(task)


@dataclass
class RetrieverAgentAdapter:
    """Adapter that fetches context via MCP search/read operations."""

    run_fetch: Callable[[TaskInput, ChangePlan], Any]

    def fetch(self, task: TaskInput, plan: ChangePlan) -> Any:
        return self.run_fetch(task, plan)


@dataclass
class CoderAgentAdapter:
    """Adapter that applies diffs and returns the resulting commit SHA."""

    run_apply: Callable[[TaskInput, ChangePlan, Any], str]

    def apply(self, task: TaskInput, plan: ChangePlan, context: Any) -> str:
        return self.run_apply(task, plan, context)


@dataclass
class RunnerAdapter:
    """Adapter around build/test execution."""

    run_ci: Callable[[TaskInput, ChangePlan, str], CIResult]

    def execute(self, task: TaskInput, plan: ChangePlan, commit: str) -> CIResult:
        return self.run_ci(task, plan, commit)


@dataclass
class PullRequestAdapter:
    """Adapter that opens pull requests and emits a URL."""

    run_open: Callable[[TaskInput, ChangePlan, str, CIResult], str]

    def open(self, task: TaskInput, plan: ChangePlan, commit: str, ci: CIResult) -> str:
        return self.run_open(task, plan, commit, ci)


@dataclass
class ReviewAdapter:
    """Adapter that handles review signals and optional fix-up cycles."""

    await_review: Callable[[TaskInput, str], ReviewResult]
    address_feedback: Optional[Callable[[TaskInput, str, ReviewResult], ReviewResult]] = None

    def resolve(self, task: TaskInput, pr_url: str) -> ReviewResult:
        return self.await_review(task, pr_url)

    def fix(self, task: TaskInput, pr_url: str, review: ReviewResult) -> ReviewResult:
        if self.address_feedback is None:
            raise RuntimeError("address_feedback callable not configured")
        return self.address_feedback(task, pr_url, review)


@dataclass
class AgentsToolkitFactory:
    """Assembles adapters into the runtime-ready AgentsToolkit."""

    planner: PlannerAgentAdapter
    retriever: RetrieverAgentAdapter
    coder: CoderAgentAdapter
    runner: RunnerAdapter
    pull_requests: PullRequestAdapter
    reviewers: ReviewAdapter

    def build(self) -> AgentsToolkit:
        return AgentsToolkit(
            plan_changes=self.planner.plan,
            fetch_context=self.retriever.fetch,
            apply_diffs=self.coder.apply,
            run_ci=self.runner.execute,
            open_pr=self.pull_requests.open,
            await_review=self.reviewers.resolve,
            address_feedback=self.reviewers.fix if self.reviewers.address_feedback else None,
        )
