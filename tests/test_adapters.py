from typing import Dict, List

from coding_agent.adapters import (
    AgentsToolkitFactory,
    CoderAgentAdapter,
    PlannerAgentAdapter,
    PullRequestAdapter,
    RetrieverAgentAdapter,
    ReviewAdapter,
    RunnerAdapter,
    TemporalAwaiter,
)
from coding_agent.adapters.temporal import ReviewSignalGateway
from coding_agent.orchestrator import CIResult, ReviewResult, TaskInput
from coding_agent.runtime import CodingAgentRuntime


class RecordingGateway(ReviewSignalGateway):
    def __init__(self, responses: List[ReviewResult]):
        self.responses = responses
        self.calls: List[str] = []

    def wait_for_review(self, task: TaskInput, pr_url: str) -> ReviewResult:
        self.calls.append(pr_url)
        return self.responses.pop(0)


def test_toolkit_factory_wires_adapters(feature_plan):
    calls: Dict[str, int] = {"plan": 0, "fetch": 0, "apply": 0, "ci": 0, "pr": 0, "review": 0, "fix": 0}

    factory = AgentsToolkitFactory(
        planner=PlannerAgentAdapter(lambda task: calls.__setitem__("plan", calls["plan"] + 1) or feature_plan),
        retriever=RetrieverAgentAdapter(lambda task, plan: calls.__setitem__("fetch", calls["fetch"] + 1) or {"files": []}),
        coder=CoderAgentAdapter(lambda task, plan, ctx: calls.__setitem__("apply", calls["apply"] + 1) or "commit"),
        runner=RunnerAdapter(lambda task, plan, commit: calls.__setitem__("ci", calls["ci"] + 1) or CIResult(passed=True)),
        pull_requests=PullRequestAdapter(lambda task, plan, commit, ci: calls.__setitem__("pr", calls["pr"] + 1) or "https://example.com/pr/5"),
        reviewers=ReviewAdapter(
            await_review=lambda task, pr: calls.__setitem__("review", calls["review"] + 1) or ReviewResult(approved=False),
            address_feedback=lambda task, pr, review: calls.__setitem__("fix", calls["fix"] + 1) or ReviewResult(approved=True),
        ),
    )

    toolkit = factory.build()
    runtime = CodingAgentRuntime(toolkit=toolkit)
    result = runtime.execute(TaskInput(ticket_id="ENG-1423", repository="repo", base_branch="main"))

    assert result.pr_url == "https://example.com/pr/5"
    assert calls == {"plan": 1, "fetch": 1, "apply": 1, "ci": 1, "pr": 1, "review": 1, "fix": 1}


def test_temporal_awaiter_uses_gateway(feature_plan):
    gateway = RecordingGateway([ReviewResult(approved=True)])
    factory = AgentsToolkitFactory(
        planner=PlannerAgentAdapter(lambda task: feature_plan),
        retriever=RetrieverAgentAdapter(lambda task, plan: {}),
        coder=CoderAgentAdapter(lambda task, plan, ctx: "commit"),
        runner=RunnerAdapter(lambda task, plan, commit: CIResult(passed=True)),
        pull_requests=PullRequestAdapter(lambda task, plan, commit, ci: "https://example.com/pr/6"),
        reviewers=ReviewAdapter(
            await_review=TemporalAwaiter(gateway=gateway).await_review,
        ),
    )

    toolkit = factory.build()
    runtime = CodingAgentRuntime(toolkit=toolkit)
    result = runtime.execute(TaskInput(ticket_id="ENG-1423", repository="repo", base_branch="main"))

    assert result.pr_url == "https://example.com/pr/6"
    assert gateway.calls == ["https://example.com/pr/6"]
