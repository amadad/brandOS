from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from coding_agent.brand.emailer import InMemoryEmailSender, ResendEmailSender
from coding_agent.brand.pipeline import BrandTask


def make_task():
    return BrandTask(brand_id="brand", report_date=date(2025, 1, 15), recipients=("to@example.com",))


def test_in_memory_email_sender_records_messages():
    sender = InMemoryEmailSender()
    message_id = sender.send(make_task(), "subject", "body")

    assert message_id == "mem-1"
    assert sender.sent_messages[0]["subject"] == "subject"


@patch("coding_agent.brand.emailer.requests.post")
def test_resend_email_sender_calls_api(mock_post: MagicMock):
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "email-123"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    sender = ResendEmailSender(api_key="key", sender="BrandOS <reports@brandos.com>")
    message_id = sender.send(make_task(), "subject", "body")

    assert message_id == "email-123"
    mock_post.assert_called_once()
    kwargs = mock_post.call_args.kwargs
    assert kwargs["headers"]["Authorization"] == "Bearer key"
