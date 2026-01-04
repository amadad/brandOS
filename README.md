# Coding Agent PRD & Reference Skeleton

## Overview
- This repository contains the execution-ready product requirements document for a coding copilot built on the OpenAI Agents SDK and Temporal, plus a lightweight Python code skeleton that expresses key contracts.
- The code follows the PRD structure: domain models (Change Plan), workflow specification scaffolding, MCP tool contracts, an orchestrator stub, adapters for Agents SDK + Temporal integration, and a runtime composition layer ready to host real services.
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
- `src/coding_agent/mcp/contracts.py` – Contracts for repo, runner, and code-search MCP tools with guardrail validation for both requests and responses.
- `src/coding_agent/orchestrator.py` – High-level orchestrator stub that sequences Activities and enforces basic guardrails.
- `src/coding_agent/adapters/` – Agent and Temporal adapter scaffolding plus a factory that produces runtime-ready toolkits.
- `src/coding_agent/runtime.py` – Runtime wiring that wraps toolkit callables, notifies observers, and returns structured run results.
- `src/coding_agent/brand/` – Brand reporting models, providers (web + Google News), relevance filtering, and persistence helpers.
- `config/brand_profiles.yaml` – Keyword/competitor/stop-phrase config consumed by the relevance gate.
- `src/coding_agent/cli.py` – Demo CLI wiring that exercises both the coding workflow and a brand-report pipeline with mock adapters.
- `tests/` – Pytest suite built first (TDD) covering each module.

## Run the demo
```
uv run python -m coding_agent.cli --pipeline coding
# or
uv run python main.py --pipeline coding
```

## Run the brand report demo
```
uv run python -m coding_agent.cli --pipeline brand
# or
uv run python main.py --pipeline brand
```

Use `--signals-file docs/sample_signals/brandos.json` to feed in the sample dataset, or point to your own JSON payload. Pass `--brand-url https://wearebarbarian.com` (or any public site) to scrape the latest headings and meta description for highlights. If that site is unreachable the pipeline automatically queries Google News for the brand name before falling back to a curated sample, so reports always include attributed sources. Tweak keywords/competitors/stop phrases in `config/brand_profiles.yaml` to keep the relevance filter sharp. To send via Resend, set `RESEND_API_KEY` (and optionally `RESEND_FROM_ADDRESS`) then run:

```
uv run python -m coding_agent.cli --pipeline brand --send-resend --resend-from "BrandOS Reports <reports@example.com>"
```

The Resend adapter posts to `https://api.resend.com/emails`; in automated tests we rely on the in-memory sender so the suite stays hermetic.

### Data retention & analytics
- Raw signals and report summaries are written to `data/reports/{brand_id}/{YYYY-MM-DD}/`.
- A Kùzu-backed knowledge store is attempted (optional); if the local query dialect is unsupported the run logs a warning and continues without failing the email send.
- Customize storage locations via `BRANDOS_DATA_ROOT` and `BRANDOS_KUZU_PATH` environment variables.

## Run tests
```
uv run pytest
```

## Repository layout
- `docs/` – Documentation and design artifacts (currently the coding agent PRD).
- `src/` – Python package housing reference contracts and orchestration skeleton.
- `tests/` – Test cases validating the contracts and guardrails; fixtures cover feature, bugfix, and refactor scenarios.
- `LICENSE` – MIT license inherited from the previous project footprint.

## Contributing
Keep new design notes or supporting specs in `docs/` and cross-link them from the PRD or this README. When expanding the code, drive each module with tests (`uv run pytest`) and keep production integrations behind injectable interfaces.

## License
Released under the MIT License. See `LICENSE` for details.
