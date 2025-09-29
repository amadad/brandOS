from coding_agent.cli import run_demo_task


def test_run_demo_task_produces_pr_url(capsys):
    pr_url = run_demo_task()

    captured = capsys.readouterr().out
    assert "PlanChanges" in captured
    assert "OpenPR" in captured
    assert pr_url.startswith("https://")
