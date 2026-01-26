# brandOS Development Guidelines

## Project Overview

CLI-first brand operations toolkit with autonomous execution. Unified personas, competitive intel, content production, evaluation, and publishing.

**Architecture**: Human-over-the-loop - humans set policies and thresholds, system operates autonomously within those boundaries, exceptions escalated.

## Project Structure

```
src/brand_os/
├── cli.py              # Main CLI entry (Typer)
├── cli_utils.py        # Output formatting helpers
├── loop.py             # Autonomous execution daemon
├── loop_cli.py         # Loop/decision/policy CLI commands
├── core/               # Shared utilities
│   ├── brands.py       # Brand config loading
│   ├── config.py       # App configuration
│   ├── decision.py     # Decision logging + audit trail
│   ├── policy.py       # Policy engine + guardrails
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

## Autonomous Loop

The system runs 24/7 in a container, processing signals and executing decisions within policy boundaries.

```bash
# Start the loop
brandos loop start                          # All brands
brandos loop start --brand acme             # Specific brand
brandos loop test acme                      # Test single cycle

# Docker deployment
docker compose up -d                        # Start container
docker compose logs -f loop                 # View logs
```

## Policy Engine

Policies define what the system can do autonomously vs. what requires human intervention.

```python
from brand_os.core.policy import evaluate_decision, PolicyVerdict

evaluation = evaluate_decision(decision)

if evaluation.verdict == PolicyVerdict.ALLOW:
    # Execute autonomously
elif evaluation.verdict == PolicyVerdict.ESCALATE:
    # Queue for human review
else:  # DENY
    # Blocked by policy
```

Policy configuration per brand in `brand.yml`:

```yaml
policy:
  enabled: true
  default_verdict: escalate
  global_min_confidence: 0.7
  always_allow: [signal_action]
  always_escalate: [budget_allocation]
  rules:
    - name: content-auto-publish
      decision_types: [content_publish]
      min_confidence: 0.8
      max_per_hour: 5
```

```bash
# Policy CLI commands
brandos policy show acme
brandos policy test acme --type content_publish --confidence 0.85
brandos policy templates
```

## Decision Management

All agent-proposed actions are logged and evaluated against policy before execution.

```bash
# View decisions
brandos decision list
brandos decision list --brand acme --status pending_review
brandos decision pending                    # Quick view of items needing review

# Human review (for escalated decisions)
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
