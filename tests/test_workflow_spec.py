from datetime import timedelta

from coding_agent.workflow_spec import (
    CodingTaskWorkflowSpec,
    WorkflowActivity,
    WorkflowSignal,
)


EXPECTED_ACTIVITY_ORDER = (
    "PlanChanges",
    "FetchContext",
    "ApplyDiffs",
    "RunCI",
    "OpenPR",
    "AwaitReview",
    "AddressFeedback",
)


def test_default_workflow_spec_has_expected_activities():
    spec = CodingTaskWorkflowSpec.default()

    assert tuple(activity.name for activity in spec.activities) == EXPECTED_ACTIVITY_ORDER
    assert all(isinstance(activity, WorkflowActivity) for activity in spec.activities)
    assert spec.sleep_timeout >= timedelta(hours=1)


def test_review_signal_present_with_description():
    spec = CodingTaskWorkflowSpec.default()

    review_signal = next((s for s in spec.signals if s.name == "review"), None)
    assert review_signal is not None
    assert isinstance(review_signal, WorkflowSignal)
    assert "resume" in review_signal.description.lower()
