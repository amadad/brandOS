from dataclasses import dataclass
from typing import Any, Dict, List

import pytest

from coding_agent.models import ChangePlan
from coding_agent.orchestrator import CIResult, ReviewResult, TaskInput
from coding_agent.runtime import AgentsToolkit, CodingAgentRuntime, ExecutionObserver, RunResult


@dataclass
class RecordingObserver:
    steps: List[str]

    def on_step(self, step: str, payload: Dict[str, Any]) -> None:
        self.steps.append(step)


def test_runtime_executes_toolkit_and_emits_steps(feature_plan: ChangePlan):
    calls: List[str] = []

    toolkit = AgentsToolkit(
        plan_changes=lambda task: calls.append("plan") or feature_plan,
        fetch_context=lambda task, p: calls.append("fetch") or {"files": []},
        apply_diffs=lambda task, p, ctx: calls.append("apply") or "commit",
        run_ci=lambda task, p, commit: calls.append("ci") or CIResult(passed=True, url="ci"),
        open_pr=lambda task, p, commit, ci: calls.append("pr") or "https://example.com/pr/1",
        await_review=lambda task, pr: calls.append("await") or ReviewResult(approved=True),
        address_feedback=None,
    )

    observer = RecordingObserver(steps=[])
    runtime = CodingAgentRuntime(toolkit=toolkit, observer=observer)

    result = runtime.execute(TaskInput(ticket_id="ENG-111", repository="repo", base_branch="main"))

    assert isinstance(result, RunResult)
    assert result.pr_url == "https://example.com/pr/1"
    assert calls == ["plan", "fetch", "apply", "ci", "pr", "await"]
    assert observer.steps == ["PlanChanges", "FetchContext", "ApplyDiffs", "RunCI", "OpenPR", "AwaitReview"]


def test_runtime_handles_review_feedback_loop(feature_plan: ChangePlan):
    feedback_calls: List[str] = []

    toolkit = AgentsToolkit(
        plan_changes=lambda task: feature_plan,
        fetch_context=lambda *a, **k: {},
        apply_diffs=lambda *a, **k: "commit",
        run_ci=lambda *a, **k: CIResult(passed=True),
        open_pr=lambda *a, **k: "https://example.com/pr/2",
        await_review=lambda *a, **k: ReviewResult(approved=False, feedback="needs tests"),
        address_feedback=lambda task, pr, review: feedback_calls.append("feedback") or ReviewResult(approved=True),
    )

    runtime = CodingAgentRuntime(toolkit=toolkit)
    result = runtime.execute(TaskInput(ticket_id="ENG-111", repository="repo", base_branch="main"))

    assert result.pr_url == "https://example.com/pr/2"
    assert feedback_calls == ["feedback"]


def test_runtime_raises_when_feedback_missing(feature_plan: ChangePlan):
    toolkit = AgentsToolkit(
        plan_changes=lambda task: feature_plan,
        fetch_context=lambda *a, **k: {},
        apply_diffs=lambda *a, **k: "commit",
        run_ci=lambda *a, **k: CIResult(passed=True),
        open_pr=lambda *a, **k: "https://example.com/pr/3",
        await_review=lambda *a, **k: ReviewResult(approved=False),
        address_feedback=None,
    )

    runtime = CodingAgentRuntime(toolkit=toolkit)

    with pytest.raises(RuntimeError):
        runtime.execute(TaskInput(ticket_id="ENG-111", repository="repo", base_branch="main"))
