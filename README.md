# Coding Agent PRD & Reference Skeleton

## Overview
- This repository contains the execution-ready product requirements document for a coding copilot built on the OpenAI Agents SDK and Temporal, plus a lightweight Python code skeleton that expresses key contracts.
- The code follows the PRD structure: domain models (Change Plan), workflow specification scaffolding, MCP tool contracts, and an orchestrator stub for sequencing Activities.
- Temporal will provide durable execution in production; the current Python modules stay pure so they can be tested rapidly while real integrations are developed.

## Read the PRD
The full specification lives at `docs/coding-agent-prd.md`. It covers:
- Goals, scope, target users, and success metrics.
- System architecture with Agents SDK services, MCP tools, and Temporal workflows.
- Functional and non-functional requirements, guardrails, data schemas, and rollout phases.
- Risks, mitigations, evaluation plans, and API sketches for integrating the agent into existing tooling.

## Code scaffolding
- `src/coding_agent/models.py` – Pydantic models for planner outputs (`ChangePlan`, `PlannedEdit`).
- `src/coding_agent/workflow_spec.py` – Pure-Python description of the Temporal workflow Activities, signals, and timeouts.
- `src/coding_agent/mcp/contracts.py` – Contracts for repo, runner, and code-search MCP tools with guardrail validation.
- `src/coding_agent/orchestrator.py` – High-level orchestrator stub that sequences Activities and enforces basic guardrails.
- `src/coding_agent/cli.py` – Demo CLI wiring that exercises the orchestrator with mock Activities.
- `tests/` – Pytest suite built first (TDD) covering each module.

## Run the demo
```
uv run python -m coding_agent.cli
```

## Run tests
```
uv run pytest
```

## Repository layout
- `docs/` – Documentation and design artifacts (currently the coding agent PRD).
- `src/` – Python package housing reference contracts and orchestration skeleton.
- `tests/` – Test cases validating the contracts and guardrails.
- `LICENSE` – MIT license inherited from the previous project footprint.

## Contributing
Keep new design notes or supporting specs in `docs/` and cross-link them from the PRD or this README. When expanding the code, drive each module with tests (`uv run pytest`) and keep production integrations behind injectable interfaces.

## License
Released under the MIT License. See `LICENSE` for details.
