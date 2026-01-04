import json

import pytest

from coding_agent.mcp.contracts import (
    CodeSearchQuery,
    CodeSearchResponse,
    CodeSearchResult,
    RepoReadRequest,
    RepoReadResponse,
    RepoWriteRequest,
    RunnerCommandRequest,
)


def test_repo_read_request_blocks_absolute_paths():
    with pytest.raises(ValueError):
        RepoReadRequest(path="/etc/passwd")


def test_repo_read_response_round_trip():
    response = RepoReadResponse(path="src/app.py", content="print('hi')", sha="abc123")
    assert response.model_dump()["sha"] == "abc123"


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


def test_code_search_response_serializes():
    query = CodeSearchQuery(query="retry logic", max_results=5)
    response = CodeSearchResponse(
        query=query,
        results=(
            CodeSearchResult(path="pkg/payments/client.py", start_line=10, end_line=20, snippet="..."),
        ),
    )

    payload = json.loads(response.model_dump_json())
    assert payload["query"]["max_results"] == 5
    assert payload["results"][0]["path"] == "pkg/payments/client.py"


def test_code_search_result_rejects_malformed_lines():
    with pytest.raises(ValueError):
        CodeSearchResult(path="pkg/x.py", start_line=5, end_line=3, snippet="...")
