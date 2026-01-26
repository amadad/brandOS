# brandOS Development Guidelines

## Project Overview

CLI-first brand operations toolkit. Unified personas, competitive intel, content production, evaluation, and publishing.

## Project Structure

```
src/brand_os/
├── cli.py              # Main CLI entry (Typer)
├── cli_utils.py        # Output formatting helpers
├── core/               # Shared utilities
│   ├── brands.py       # Brand config loading
│   ├── config.py       # App configuration
│   ├── decision.py     # Decision logging + audit trail
│   ├── llm.py          # LLM interface
│   ├── signals.py      # Signal utilities
│   └── storage.py      # Storage paths
├── signals/            # Signal ingestion pipeline
│   └── schema.py       # Unified Signal model
├── workflows/          # Approval workflows
│   └── approval.py     # State machine for decisions
├── agents/             # Specialized AI agents
│   ├── base.py         # Base Agent protocol
│   ├── market.py       # Market analyst
│   └── threat.py       # Threat assessor
├── persona/            # Persona management
├── intel/              # Competitive intelligence
├── produce/            # Content production
├── eval/               # Content evaluation
├── publish/            # Social publishing
└── server/             # API + MCP server

brands/                 # Brand configurations
├── _template/          # Default template
└── <brand>/
    ├── brand.yml       # Core config (always loaded)
    ├── rubric.yml      # Evaluation criteria
    ├── references/     # Detailed docs (loaded as needed)
    └── assets/         # Logos, templates
```

## Build & Test Commands

```bash
# Install dependencies
uv sync                      # Core only
uv sync --all-extras         # Everything
uv sync --extra workflows    # Phase 1 features

# Development
uv run brandos --help        # Run CLI
uv run pytest                # Run tests
uv run ruff check src/       # Lint
uv run ruff format src/      # Format
```

## Coding Conventions

- **Language**: Python 3.11+, strict typing, Pydantic models
- **CLI**: Typer with Rich for output formatting
- **Async**: Use async/await for I/O operations
- **Files**: Keep under 500 LOC; split when larger
- **Comments**: Brief comments for non-obvious logic only

## Decision Logging

All agent-proposed actions MUST be logged before execution:

```python
from brand_os.core.decision import Decision, DecisionType, log_decision

decision = Decision(
    type=DecisionType.CONTENT_PUBLISH,
    brand="acme",
    proposal={"content": "...", "platform": "twitter"},
    rationale="High engagement predicted based on competitor analysis",
    confidence=0.85,
)
await log_decision(decision)
```

High-stakes actions require human approval via the approval workflow.

## Multi-Agent Safety

When multiple agents run concurrently:

- Each agent gets a unique session ID
- Decisions logged with agent attribution
- Never modify another agent's pending decisions
- Use `git add <specific-files>` not `git add .`
- Scope commits to own work only

## Signal Processing

All external data normalized to Signal schema before processing:

```python
from brand_os.signals.schema import Signal

signal = Signal(
    source="news",
    brand="acme",
    signal_type="competitor_mention",
    content="...",
    relevance_score=0.8,
    urgency="medium",
)
```

## Approval Workflow

High-stakes actions follow: `draft → pending_review → approved/rejected → executed`

```bash
# CLI approval commands
brandos decision list --status pending
brandos decision approve <id> --reason "LGTM"
brandos decision reject <id> --reason "Too risky"
```

## Guardrails

- Never publish without human approval for new brands
- Never commit API keys or credentials
- Never use `rm`; use `trash` instead
- Test coverage required for core modules
- Run `ruff check && ruff format` before commits

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GOOGLE_API_KEY` | Gemini LLM |
| `ANTHROPIC_API_KEY` | Claude LLM |
| `OPENAI_API_KEY` | OpenAI/LiteLLM |
| `SLACK_WEBHOOK_URL` | Approval notifications |

## Testing

```bash
uv run pytest                        # All tests
uv run pytest tests/core/            # Core module only
uv run pytest -k "decision"          # Pattern match
uv run pytest --cov=brand_os         # With coverage
```
