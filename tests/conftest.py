import pytest

from coding_agent.models import ChangePlan


@pytest.fixture
def feature_plan() -> ChangePlan:
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


@pytest.fixture
def bugfix_plan() -> ChangePlan:
    return ChangePlan.model_validate(
        {
            "ticket_id": "BUG-1001",
            "goal": "Fix payment timeout bug",
            "constraints": ["add regression test"],
            "edits": [
                {"path": "pkg/payments/retry.py", "intent": "adjust timeout"},
                {"path": "tests/test_retry.py", "intent": "add failing test"},
            ],
            "risk": ["retry storm"],
            "checks": ["pytest -k retry"],
        }
    )


@pytest.fixture
def refactor_plan() -> ChangePlan:
    return ChangePlan.model_validate(
        {
            "ticket_id": "ENG-2042",
            "goal": "Refactor client for better separation",
            "constraints": ["no API change", "maintain coverage"],
            "edits": [
                {"path": "pkg/payments/client.py", "intent": "extract interface"},
                {"path": "pkg/payments/adapters.py", "intent": "add adapter"},
                {"path": "tests/test_payments_client.py", "intent": "update tests"},
            ],
            "risk": ["interface drift"],
            "checks": ["pytest -k payments", "lint"],
        }
    )
