from pathlib import Path
from unittest.mock import patch

from coding_agent.cli import run_brand_report_demo, run_demo_task


def test_run_demo_task_produces_pr_url(capsys):
    pr_url = run_demo_task()

    captured = capsys.readouterr().out
    assert "PlanChanges" in captured
    assert "OpenPR" in captured
    assert pr_url.startswith("https://")


def test_run_brand_report_demo_outputs_email(capsys):
    with patch(
        "coding_agent.cli.persist_raw_signals", return_value=Path("/tmp/signals.json")
    ) as persist_raw, patch(
        "coding_agent.cli.persist_report_summary", return_value=Path("/tmp/summary.json")
    ) as persist_summary, patch("coding_agent.cli.persist_to_kuzu") as persist_kuzu:
        message_id = run_brand_report_demo()

    persist_raw.assert_called_once()
    persist_summary.assert_called_once()
    persist_kuzu.assert_called_once()
    captured = capsys.readouterr().out
    assert "BrandReport" in captured
    assert message_id.startswith("mem-")
