# brandOS Agent Architecture

## Overview

brandOS uses specialized AI agents that process signals and propose decisions. Each agent focuses on a specific domain while sharing a common interface for orchestration.

## Agent Protocol

All agents implement the `Agent` protocol:

```python
class Agent(Protocol):
    @property
    def agent_id(self) -> str: ...

    @property
    def description(self) -> str: ...

    @property
    def decision_types(self) -> list[DecisionType]: ...

    async def process(self, context: AgentContext) -> AgentResult: ...
```

## Data Flow

```
Signals → AgentContext → Agent.process() → AgentResult → Decisions
                                                              ↓
                                                    Human Approval
                                                              ↓
                                                        Execution
```

## Core Agents

### Market Analyst (`market-analyst`)

**Purpose**: Analyze market signals for trends and opportunities.

**Inputs**:
- Financial signals (stock prices, currency)
- Competitor signals (product launches, announcements)
- News signals (industry coverage)

**Outputs**:
- Trend analysis
- Opportunity identification
- Campaign adjustment proposals

**Decision Types**:
- `CAMPAIGN_ADJUSTMENT`
- `SIGNAL_ACTION`

### Threat Assessor (`threat-assessor`)

**Purpose**: Identify risks, threats, and potential crises.

**Inputs**:
- Sentiment signals (negative mentions)
- Competitor signals (competitive threats)
- Regulatory signals (compliance risks)

**Outputs**:
- Threat level assessment
- Vulnerability analysis
- Response recommendations

**Decision Types**:
- `THREAT_RESPONSE`
- `ALERT_ESCALATION`

### Content Producer (`content-producer`)

**Purpose**: Generate brand-aligned content based on analysis.

**Inputs**:
- Market analysis results
- Brand voice configuration
- Platform constraints

**Outputs**:
- Platform-specific content
- Publishing recommendations

**Decision Types**:
- `CONTENT_PUBLISH`
- `CONTENT_SCHEDULE`

## AgentContext

Context provided to agents for processing:

```python
class AgentContext(BaseModel):
    session_id: str          # Unique session for this run
    brand: str               # Target brand
    signals: list[Signal]    # Signals to process
    parameters: dict         # Agent-specific parameters
    history: list[dict]      # Previous analysis results
```

## AgentResult

Result returned by agents:

```python
class AgentResult(BaseModel):
    agent_id: str
    session_id: str
    timestamp: datetime
    analysis: dict           # Agent-specific analysis
    summary: str             # Human-readable summary
    decisions: list[Decision]  # Proposed decisions
    signals_processed: int
    confidence: float
    errors: list[str]
```

## Multi-Agent Coordination

### Parallel Execution

Agents can run in parallel on the same signals:

```
                    ┌─────────────────┐
                    │    Signals      │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │ Market Analyst│ │Threat Assessor│ │Content Producer│
    └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              ▼
                    ┌─────────────────┐
                    │   Aggregator    │
                    │  (merge results)│
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │ Human Approval  │
                    └─────────────────┘
```

### Session Isolation

Each agent run gets a unique session ID:

- Decisions attributed to `agent_id + session_id`
- Audit trail tracks which agent proposed what
- No cross-contamination between concurrent runs

### Conflict Resolution

When agents propose conflicting decisions:

1. Higher confidence wins (configurable)
2. More specific decision type wins
3. Human reviewer decides ties

## CLI Usage

```bash
# Run single agent
brandos agent run market-analyst --brand acme

# Run all agents on latest signals
brandos agent run-all --brand acme

# Interactive agent chat
brandos agent chat market-analyst --brand acme
```

## Implementation Notes

### Using PydanticAI (Recommended)

```python
from pydantic_ai import Agent

market_agent = Agent(
    'anthropic:claude-sonnet-4-20250514',
    system_prompt="You are a market analyst...",
    result_type=MarketAnalysis
)

result = await market_agent.run(context.model_dump_json())
```

### Using Direct LLM Calls

```python
from brand_os.core.llm import complete_json

analysis = await complete_json(
    prompt=f"Analyze these signals: {signals}",
    default={"trends": [], "opportunities": []},
    model="gemini-2.0-flash"
)
```

## Future Agents

Planned additions:

- **Supply Chain Monitor**: Track vendor/logistics signals
- **Budget Optimizer**: Allocate resources based on performance
- **Compliance Checker**: Monitor regulatory requirements
- **Audience Analyzer**: Track demographic/psychographic shifts
