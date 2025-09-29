import pytest

from coding_agent.mcp.contracts import (
    CodeSearchQuery,
    RepoWriteRequest,
    RunnerCommandRequest,
)


def test_repo_write_rejects_parent_directory_escape():
    with pytest.raises(ValueError):
        RepoWriteRequest(path="../secrets.env", content="token")


def test_repo_write_allows_relative_paths():
    request = RepoWriteRequest(path="src/module.py", content="# change")
    assert request.path == "src/module.py"
    assert request.allow_create is False


def test_runner_command_requires_tokens():
    with pytest.raises(ValueError):
        RunnerCommandRequest(command=[])

    request = RunnerCommandRequest(command=["pytest", "-k", "agent"], timeout_seconds=900)
    assert request.timeout_seconds == 900


def test_code_search_query_defaults():
    query = CodeSearchQuery(query="retry logic")
    assert query.max_results == 20
    assert query.repo_filter is None
