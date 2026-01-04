"""Email delivery adapters for brand reports."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

import requests

from coding_agent.brand.pipeline import BrandTask


class EmailSender:
    """Interface for sending brand report emails."""

    def send(self, task: BrandTask, subject: str, body: str) -> str:
        raise NotImplementedError


@dataclass
class InMemoryEmailSender(EmailSender):
    """Collects emails in memory (useful for tests)."""

    sent_messages: List[dict] = field(default_factory=list)

    def send(self, task: BrandTask, subject: str, body: str) -> str:
        message_id = f"mem-{len(self.sent_messages) + 1}"
        self.sent_messages.append(
            {
                "task": task,
                "subject": subject,
                "body": body,
                "message_id": message_id,
            }
        )
        return message_id


@dataclass
class ResendEmailSender(EmailSender):
    """Sends emails via the Resend API."""

    api_key: str
    sender: str

    def send(self, task: BrandTask, subject: str, body: str) -> str:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "from": self.sender,
            "to": list(task.recipients),
            "subject": subject,
            "text": body,
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("id", "")


def build_resend_from_env(sender: str | None = None) -> ResendEmailSender:
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise RuntimeError("RESEND_API_KEY environment variable not set")
    from_address = sender or os.environ.get("RESEND_FROM_ADDRESS")
    if not from_address:
        raise RuntimeError("Resend sender address not provided")
    return ResendEmailSender(api_key=api_key, sender=from_address)
