import pytest

from coding_agent.models import ChangePlan, PlannedEdit
from coding_agent.orchestrator import (
    CIResult,
    CodingTaskOrchestrator,
    ReviewResult,
    TaskInput,
)


def test_orchestrator_runs_happy_path_in_order(feature_plan: ChangePlan):
    calls = []
    task = TaskInput(ticket_id=feature_plan.ticket_id, repository="git@example/repo", base_branch="main")

    orchestrator = CodingTaskOrchestrator(
        plan_changes=lambda t: calls.append("plan") or feature_plan,
        fetch_context=lambda t, p: calls.append("fetch") or {"files": []},
        apply_diffs=lambda t, p, ctx: calls.append("apply") or "commit-sha",
        run_ci=lambda t, plan, commit: calls.append("ci") or CIResult(passed=True, url="ci"),
        open_pr=lambda t, plan, commit, ci: calls.append("pr") or "https://example.com/pr/1",
        await_review=lambda t, pr: calls.append("await") or ReviewResult(approved=True),
        address_feedback=lambda *args, **kwargs: calls.append("feedback"),
    )

    pr_url = orchestrator.run(task)

    assert pr_url == "https://example.com/pr/1"
    assert calls == ["plan", "fetch", "apply", "ci", "pr", "await"]


def test_guardrail_requires_test_related_check():
    task = TaskInput(ticket_id="ENG-99", repository="git@example/repo", base_branch="main")
    plan_no_tests = ChangePlan(
        ticket_id="ENG-99",
        goal="Do something risky",
        constraints=("no test",),
        edits=(
            PlannedEdit(path="src/app.py", intent="change behavior"),
        ),
        risk=("regression",),
        checks=(),
    )

    orchestrator = CodingTaskOrchestrator(
        plan_changes=lambda t: plan_no_tests,
        fetch_context=lambda *a, **k: None,
        apply_diffs=lambda *a, **k: "commit-sha",
        run_ci=lambda *a, **k: CIResult(passed=True),
        open_pr=lambda *a, **k: "pr",
        await_review=lambda *a, **k: ReviewResult(approved=True),
        address_feedback=lambda *a, **k: None,
    )

    with pytest.raises(ValueError):
        orchestrator.run(task)
