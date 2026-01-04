"""Runtime composition for the coding agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Protocol

from coding_agent.models import ChangePlan
from coding_agent.orchestrator import CIResult, CodingTaskOrchestrator, ReviewResult, TaskInput


class ExecutionObserver(Protocol):
    """Observer that reacts to each orchestration step."""

    def on_step(self, step: str, payload: Dict[str, Any]) -> None: ...


@dataclass(frozen=True)
class AgentsToolkit:
    """Collection of callables that back agent-driven Activities."""

    plan_changes: Callable[[TaskInput], ChangePlan]
    fetch_context: Callable[[TaskInput, ChangePlan], Any]
    apply_diffs: Callable[[TaskInput, ChangePlan, Any], str]
    run_ci: Callable[[TaskInput, ChangePlan, str], CIResult]
    open_pr: Callable[[TaskInput, ChangePlan, str, CIResult], str]
    await_review: Callable[[TaskInput, str], ReviewResult]
    address_feedback: Optional[Callable[[TaskInput, str, ReviewResult], ReviewResult]] = None


@dataclass(frozen=True)
class RunResult:
    """Aggregate of the important outputs from a run."""

    plan: ChangePlan
    commit_sha: str
    ci_result: CIResult
    pr_url: str


@dataclass
class CodingAgentRuntime:
    """Binds toolkit callables into the orchestrator and surfaces lifecycle notifications."""

    toolkit: AgentsToolkit
    observer: Optional[ExecutionObserver] = None

    def execute(self, task: TaskInput) -> RunResult:
        plan_holder: Dict[str, Any] = {}
        commit_holder: Dict[str, str] = {}
        ci_holder: Dict[str, CIResult] = {}

        def notify(step: str, payload: Dict[str, Any]) -> None:
            if self.observer is not None:
                self.observer.on_step(step, payload)

        def plan_changes(task_input: TaskInput) -> ChangePlan:
            notify("PlanChanges", {"ticket_id": task_input.ticket_id})
            plan = self.toolkit.plan_changes(task_input)
            plan_holder["plan"] = plan
            return plan

        def fetch_context(task_input: TaskInput, plan: ChangePlan) -> Any:
            notify("FetchContext", {"edits": len(plan.edits)})
            return self.toolkit.fetch_context(task_input, plan)

        def apply_diffs(task_input: TaskInput, plan: ChangePlan, context: Any) -> str:
            notify("ApplyDiffs", {"files": getattr(context, "files", context)})
            commit_sha = self.toolkit.apply_diffs(task_input, plan, context)
            commit_holder["commit"] = commit_sha
            return commit_sha

        def run_ci(task_input: TaskInput, plan: ChangePlan, commit_sha: str) -> CIResult:
            notify("RunCI", {"commit": commit_sha})
            ci_result = self.toolkit.run_ci(task_input, plan, commit_sha)
            ci_holder["ci"] = ci_result
            return ci_result

        def open_pr(
            task_input: TaskInput,
            plan: ChangePlan,
            commit_sha: str,
            ci_result: CIResult,
        ) -> str:
            notify("OpenPR", {"ci_url": ci_result.url})
            return self.toolkit.open_pr(task_input, plan, commit_sha, ci_result)

        def await_review(task_input: TaskInput, pr_url: str) -> ReviewResult:
            notify("AwaitReview", {"pr_url": pr_url})
            return self.toolkit.await_review(task_input, pr_url)

        def address_feedback(
            task_input: TaskInput, pr_url: str, review_result: ReviewResult
        ) -> ReviewResult:
            notify("AddressFeedback", {"feedback": review_result.feedback})
            if self.toolkit.address_feedback is None:
                raise RuntimeError("address_feedback toolkit callable not configured")
            return self.toolkit.address_feedback(task_input, pr_url, review_result)

        orchestrator = CodingTaskOrchestrator(
            plan_changes=plan_changes,
            fetch_context=fetch_context,
            apply_diffs=apply_diffs,
            run_ci=run_ci,
            open_pr=open_pr,
            await_review=await_review,
            address_feedback=address_feedback if self.toolkit.address_feedback else None,
        )

        pr_url = orchestrator.run(task)
        plan = plan_holder.get("plan")
        commit = commit_holder.get("commit", "")
        ci_result = ci_holder.get("ci")

        if plan is None or ci_result is None:
            raise RuntimeError("runtime execution did not capture required artifacts")

        return RunResult(
            plan=plan,
            commit_sha=commit,
            ci_result=ci_result,
            pr_url=pr_url,
        )
