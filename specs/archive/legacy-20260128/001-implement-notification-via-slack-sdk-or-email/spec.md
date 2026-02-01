# [FIX] Implement notification in approval.py

## Task
In `src/brand_os/workflows/approval.py` line 114, replace the TODO comment with actual Slack notification code.

## Current Code (line 112-115)
```python
        def _notify(self, message: str) -> None:
            """Send notification (placeholder for Slack/email integration)."""
            # TODO: Implement notification via slack-sdk or email
            pass
```

## Required Change
Replace the TODO and `pass` with code that sends a Slack webhook notification using httpx (already imported in the project). Use env var `SLACK_WEBHOOK_URL`. If not set, just log the message.

## Example Implementation
```python
        def _notify(self, message: str) -> None:
            """Send notification via Slack webhook."""
            import os
            webhook_url = os.getenv("SLACK_WEBHOOK_URL")
            if webhook_url:
                try:
                    import httpx
                    httpx.post(webhook_url, json={"text": f"[BrandOS] {message}"}, timeout=10)
                except Exception:
                    pass  # Silent fail - notification is best-effort
```

## Completion Signal
```bash
grep -rn "# TODO: Implement notification via slack-sdk or email" src/brand_os/workflows/approval.py && exit 1 || echo "TODO resolved"
```

## Constraints
- Only modify the `_notify` method
- Keep it simple - just Slack webhook, no email
