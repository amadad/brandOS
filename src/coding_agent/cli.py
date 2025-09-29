"""Simple CLI demo that exercises the orchestrator wiring."""

from __future__ import annotations

from typing import Any, Dict

from coding_agent.models import ChangePlan
from coding_agent.orchestrator import CIResult, CodingTaskOrchestrator, ReviewResult, TaskInput


def _demo_plan() -> ChangePlan:
    return ChangePlan.model_validate(
        {
            "ticket_id": "ENG-1423",
            "goal": "Add retries to payment client",
            "constraints": ["no API change", "add unit tests"],
            "edits": [
                {"path": "pkg/payments/client.py", "intent": "wrap calls with retry"},
                {"path": "tests/test_payments_client.py", "intent": "add flaky API test"},
            ],
            "risk": ["timeout propagation", "idempotency"],
            "checks": ["pytest -k payments", "lint"],
        }
    )


def run_demo_task() -> str:
    """Run the orchestrator with demo callables and surface the PR URL."""

    def log(step: str, detail: str) -> None:
        print(f"{step}: {detail}")

    def plan_changes(task: TaskInput) -> ChangePlan:
        log("PlanChanges", f"ticket={task.ticket_id}")
        return _demo_plan()

    def fetch_context(task: TaskInput, plan: ChangePlan) -> Dict[str, Any]:
        log("FetchContext", f"edits={len(plan.edits)}")
        return {"files": [edit.path for edit in plan.edits]}

    def apply_diffs(task: TaskInput, plan: ChangePlan, context: Dict[str, Any]) -> str:
        log("ApplyDiffs", f"files={context['files']}")
        return "demo-commit-sha"

    def run_ci(task: TaskInput, plan: ChangePlan, commit: str) -> CIResult:
        log("RunCI", f"commit={commit}")
        return CIResult(passed=True, url="https://ci.example/jobs/123")

    def open_pr(task: TaskInput, plan: ChangePlan, commit: str, ci: CIResult) -> str:
        log("OpenPR", f"ci={ci.url}")
        return f"https://git.example/{task.ticket_id}/pull/1"

    def await_review(task: TaskInput, pr_url: str) -> ReviewResult:
        log("AwaitReview", f"url={pr_url}")
        return ReviewResult(approved=True)

    orchestrator = CodingTaskOrchestrator(
        plan_changes=plan_changes,
        fetch_context=fetch_context,
        apply_diffs=apply_diffs,
        run_ci=run_ci,
        open_pr=open_pr,
        await_review=await_review,
    )

    pr_url = orchestrator.run(
        TaskInput(ticket_id="ENG-1423", repository="git@example/repo", base_branch="main")
    )
    print(f"PR ready at {pr_url}")
    return pr_url


def main() -> None:
    run_demo_task()


if __name__ == "__main__":  # pragma: no cover
    main()
