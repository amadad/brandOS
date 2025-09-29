import json

import pytest

from coding_agent.models import ChangePlan


SAMPLE_CHANGE_PLAN = {
    "ticket_id": "ENG-1423",
    "goal": "Add retries to payment client",
    "constraints": ["no API change", "add unit+integration tests"],
    "edits": [
        {"path": "pkg/payments/client.py", "intent": "wrap calls with retry"},
        {
            "path": "tests/test_payments_client.py",
            "intent": "add flaky API test",
        },
    ],
    "risk": ["timeout propagation", "idempotency"],
    "checks": ["lint", "pytest -k payments", "coverage>75%"],
}


def test_change_plan_round_trip():
    plan = ChangePlan.model_validate(SAMPLE_CHANGE_PLAN)

    assert plan.ticket_id == "ENG-1423"
    assert plan.edits[0].path.endswith("client.py")
    assert plan.checks == ("lint", "pytest -k payments", "coverage>75%")

    as_json = json.loads(plan.model_dump_json())
    assert as_json == SAMPLE_CHANGE_PLAN


def test_change_plan_requires_intent():
    invalid_payload = {
        **SAMPLE_CHANGE_PLAN,
        "edits": [
            {"path": "pkg/payments/client.py"},
        ],
    }

    with pytest.raises(ValueError):
        ChangePlan.model_validate(invalid_payload)
