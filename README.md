# brandOS

A CLI-first toolkit for managing brand identity, competitive intelligence, content production, and social publishing—all from your terminal.

brandOS treats brands as code: version-controlled configurations, reproducible content pipelines, and automated quality gates. Instead of scattered tools and manual processes, you get a unified system where brand guidelines inform every piece of content.

## Why brandOS?

**The Problem**: Brand management is fragmented. Voice guidelines live in PDFs nobody reads. Content creation happens in silos. Publishing requires logging into five different platforms. Quality is inconsistent.

**The Solution**: brandOS unifies the entire brand operations pipeline:

```
brand.yml → persona → intel → plan → produce → eval → publish → monitor
     ↑                                          ↓
     └──────────── learnings ←─────────────────┘
```

Each stage feeds into the next. Intelligence informs strategy. Strategy shapes content. Evaluation catches drift. Learnings improve future output.

## Installation

```bash
# Install with uv (recommended)
uv sync

# Install all optional dependencies
uv sync --all-extras

# Or install specific capabilities
uv sync --extra persona    # AI persona generation
uv sync --extra intel      # Competitive scraping
uv sync --extra publish    # Social publishing
uv sync --extra video      # Video generation
```

## Quick Start

```bash
# 1. Initialize a new brand
brandos brand init acme

# 2. Create a brand persona
brandos persona create "A friendly B2B SaaS brand focused on developer tools" --as acme-voice

# 3. Generate content
brandos produce copy "Launching our new API" --brand acme --platform twitter

# 4. Evaluate against brand guidelines
brandos eval grade brands/acme/rubric.yml "Your draft content here"

# 5. Queue and publish
brandos queue add "Your approved content" --brand acme --platform twitter
brandos publish post --brand acme
```

## Core Concepts

### Brands as Configuration

Every brand is a directory with declarative config files:

```
brands/
└── acme/
    ├── brand.yml      # Voice, visual, platform config
    ├── rubric.yml     # Quality evaluation criteria
    └── assets/        # Logos, fonts, reference images
```

```yaml
# brand.yml
name: acme
description: "Developer tools that spark joy"

voice:
  tone: friendly
  vocabulary: technical
  patterns:
    - "We believe..."
    - "Here's the thing:"
  avoid_phrases:
    - "revolutionary"
    - "game-changing"

platforms:
  twitter:
    enabled: true
    max_length: 280
  linkedin:
    enabled: true
    max_length: 3000
```

### Personas

Personas are AI-generated brand voices that can be used for content generation, chat interfaces, and consistency testing.

```bash
# Create from description
brandos persona create "A witty tech journalist who explains complex topics simply"

# Create from a real person's writing style
brandos persona create "Paul Graham" --from-person

# Create from a professional role
brandos persona create "Senior DevRel Engineer" --from-role

# Chat interactively
brandos persona chat my-persona

# Export to different formats
brandos persona export my-persona --to system_prompt
brandos persona export my-persona --to ollama
```

### Evaluation Rubrics

Define quality gates with weighted dimensions:

```yaml
# rubric.yml
name: content-quality
pass_threshold: 0.7

dimensions:
  - name: clarity
    description: Is the content clear and easy to understand?
    weight: 1.0
    threshold: 0.7

  - name: brand_voice
    description: Does it match our established voice?
    weight: 1.2
    threshold: 0.8

  - name: engagement
    description: Will this resonate with our audience?
    weight: 1.0
    threshold: 0.7

red_flags:
  - Offensive content
  - Competitor mentions
  - Unverified claims
```

## Command Reference

### Brand Management

```bash
brandos brand init <name>        # Create new brand from template
brandos brand list               # List all brands
brandos brand show <name>        # Display brand config
brandos brand edit <name>        # Open config in editor
brandos brand validate <name>    # Validate brand configuration
```

### Persona Operations

```bash
brandos persona create <desc>    # Generate persona with AI
brandos persona list             # List available personas
brandos persona show <name>      # Display persona details
brandos persona chat <name>      # Interactive conversation
brandos persona ask <name> <q>   # One-shot query
brandos persona export <name>    # Export to various formats
brandos persona enrich <name>    # Enrich with external data
brandos persona mix <a> <b>      # Blend two personas
brandos persona test <name>      # Test consistency
brandos persona optimize <name>  # Automated improvement
brandos persona drift <name>     # Check for voice drift
brandos persona learn <name>     # Generate improvements from history
```

### Competitive Intelligence

```bash
brandos intel scrape <brand>     # Scrape competitor content
brandos intel analyze <brand>    # Extract patterns and hooks
brandos intel hooks <brand>      # List discovered hooks
brandos intel outliers <brand>   # Find standout content
```

### Signal Monitoring

```bash
brandos signals fetch <brand>    # Fetch latest signals
brandos signals filter <file>    # Filter by keywords
brandos signals relevance <q>    # Score signal relevance
```

### Marketing Planning

```bash
brandos plan outline <brief>     # Generate plan outline
brandos plan research <brand>    # Research stage
brandos plan strategy <brand>    # Strategy stage
brandos plan creative <brand>    # Creative stage
brandos plan activation <brand>  # Activation stage
```

### Content Production

```bash
brandos produce copy <topic>     # Generate platform copy
brandos produce thread <topic>   # Generate Twitter thread
brandos produce image <prompt>   # Generate image
brandos produce video <brief>    # Generate video
brandos produce explore <topic>  # Full multi-platform flow
```

### Content Evaluation

```bash
brandos eval grade <rubric> <content>   # Grade against rubric
brandos eval heal <brand> <content>     # Auto-fix issues
brandos eval learnings <brand>          # View accumulated learnings
```

### Publishing

```bash
brandos publish post --brand <b>        # Post from queue
brandos publish platforms               # List platform status

brandos queue add <content> --brand <b> # Add to queue
brandos queue list --brand <b>          # View queue
brandos queue show <id> --brand <b>     # Item details
brandos queue clear --brand <b>         # Clear queue
```

### Monitoring

```bash
brandos monitor report <brand>   # Generate brand report
brandos monitor email <brand>    # Send report via email
```

### Configuration

```bash
brandos config env               # Check environment variables
brandos config profiles          # Show current configuration
```

## Architecture

```
src/brand_os/
├── cli.py              # Main CLI entry point
├── loop.py             # Autonomous execution daemon
├── loop_cli.py         # Loop/decision/policy CLI
├── core/               # Shared utilities
│   ├── brands.py       # Brand loading and discovery
│   ├── config.py       # Configuration management
│   ├── decision.py     # Decision logging + audit trail
│   ├── policy.py       # Policy engine + guardrails
│   ├── learning.py     # Outcome tracking + metrics
│   ├── llm.py          # LLM interface (Gemini, Anthropic)
│   └── storage.py      # Storage paths
│
├── agents/             # Specialized AI agents
│   ├── base.py         # Agent protocol + BaseAgent
│   ├── market.py       # Market analyst (LLM-powered)
│   └── threat.py       # Threat assessor
│
├── actions/            # Execution targets
│   ├── write.py        # File output (audit trail)
│   └── notify.py       # Slack/email notifications
│
├── workflows/          # Approval workflows
│   └── approval.py     # State machine for decisions
│
├── adapters/           # Format converters
│   ├── brandos.py      # Internal format
│   ├── persona.py      # Persona format
│   └── social.py       # Social platform formats
│
├── persona/            # Persona management
│   ├── bootstrap.py    # Initial generation
│   ├── chat.py         # Conversation interface
│   ├── crud.py         # CRUD operations
│   ├── drift.py        # Drift detection
│   ├── enrichment.py   # External data enrichment
│   ├── exporters.py    # Format exporters
│   ├── learning.py     # Improvement suggestions
│   └── optimization.py # DSPy/GEPA optimization
│
├── intel/              # Competitive intelligence
│   ├── pipeline.py     # Scraping pipeline
│   ├── hooks.py        # Hook extraction
│   ├── outliers.py     # Outlier detection
│   └── scrapers/       # Platform scrapers
│
├── signals/            # Signal ingestion
│   ├── schema.py       # Unified Signal model
│   ├── relevance.py    # Relevance scoring
│   ├── history.py      # Signal history
│   └── sources/        # Data sources for loop
│       ├── rss.py      # RSS/Atom feeds
│       └── reddit.py   # Reddit posts
│
├── plan/               # Marketing planning
│   ├── stages/         # Planning stages
│   └── plugins/        # SEO, social plugins
│
├── produce/            # Content production
│   ├── copy.py         # Text generation
│   ├── queue.py        # Production queue
│   ├── image/          # Image generation
│   │   └── providers/  # Gemini, Reve
│   └── video/          # Video generation
│       └── providers/  # Replicate, Cartesia
│
├── eval/               # Evaluation
│   ├── grader.py       # Rubric grading
│   ├── heal.py         # Auto-fixing
│   ├── learnings.py    # Learning accumulation
│   └── rubric.py       # Rubric parsing
│
├── publish/            # Social publishing
│   ├── queue.py        # Publishing queue
│   ├── rate_limit.py   # Rate limiting
│   └── platforms/      # Platform publishers
│
├── monitor/            # Monitoring
│   ├── reports.py      # Report generation
│   └── emailer.py      # Email delivery
│
└── server/             # API server
    ├── api.py          # FastAPI REST API
    └── mcp.py          # MCP server
```

## Environment Variables

| Variable | Purpose | Required For |
|----------|---------|--------------|
| `GOOGLE_API_KEY` | Gemini LLM and image generation | Core features |
| `OPENAI_API_KEY` | OpenAI/LiteLLM models | Alternative LLM |
| `ANTHROPIC_API_KEY` | Anthropic Claude models | Alternative LLM |
| `EXA_API_KEY` | Persona enrichment | `persona enrich` |
| `APIFY_TOKEN` | Web scraping | `intel scrape` |
| `TWITTER_CONSUMER_KEY` | Twitter publishing | `publish` (Twitter) |
| `TWITTER_CONSUMER_SECRET` | Twitter publishing | `publish` (Twitter) |
| `TWITTER_ACCESS_TOKEN` | Twitter publishing | `publish` (Twitter) |
| `TWITTER_ACCESS_SECRET` | Twitter publishing | `publish` (Twitter) |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn publishing | `publish` (LinkedIn) |
| `RESEND_API_KEY` | Email reports | `monitor email` |

Check your configuration:

```bash
brandos config env
```

## Workflows

### Daily Content Pipeline

```bash
# Morning: gather intelligence
brandos signals fetch acme
brandos intel analyze acme

# Midday: produce content
brandos produce explore "Today's key insight" --brand acme --platforms twitter,linkedin

# Review queue
brandos queue list --brand acme

# Evaluate before publishing
brandos eval grade brands/acme/rubric.yml "$(brandos queue show abc123 --brand acme -f json | jq -r .content)"

# Publish
brandos publish post --brand acme --all
```

### Brand Launch

```bash
# Setup
brandos brand init newbrand
brandos persona create "Description of new brand voice" --as newbrand-voice

# Define quality standards
# Edit brands/newbrand/rubric.yml

# Generate launch content
brandos plan outline "Product launch for developer audience"
brandos produce thread "Introducing our new product" --brand newbrand

# Test persona consistency
brandos persona test newbrand-voice
```

### Competitive Analysis

```bash
# Scrape competitors
brandos intel scrape acme

# Find what's working for them
brandos intel hooks acme
brandos intel outliers acme

# Apply learnings to your content
brandos produce copy "Similar topic" --brand acme
```

## API Server

Run the REST API for integrations:

```bash
# Install server dependencies
uv sync --extra server

# Start server
uvicorn brand_os.server.api:app --reload
```

Or use the MCP server for AI assistant integration:

```bash
python -m brand_os.server.mcp
```

## Autonomous Loop (24/7 Operation)

brandOS can run autonomously, continuously monitoring signals and generating analysis.

### Quick Deploy

```bash
# 1. Clone
git clone https://github.com/amadad/brandOS.git
cd brandOS

# 2. Set API key (required for LLM analysis)
export GOOGLE_API_KEY=your_gemini_key

# 3. Install and create a brand
uv sync
brandos brand init mycompany

# 4. Configure the brand
nano brands/mycompany/brand.yml
```

Add to `brand.yml`:
```yaml
name: mycompany
industry: "B2B SaaS"
target_audience: "CTOs at mid-size companies"
keywords:
  - AI
  - automation
  - enterprise
```

```bash
# 5. Discover relevant subreddits (optional)
brandos signals discover-subreddits --brand mycompany

# 6. Start the loop
brandos loop start
```

### Docker Deployment

```bash
# Create brand first (required)
uv sync && brandos brand init mycompany
# Edit brands/mycompany/brand.yml

# Create .env file
echo "GOOGLE_API_KEY=your_key" > .env
echo "SLACK_WEBHOOK_URL=your_webhook" >> .env  # optional

# Run
docker compose up -d

# View logs
docker compose logs -f loop
```

### What the Loop Does

Each cycle (default: 5 minutes):
1. **Fetches signals** from RSS feeds and Reddit
2. **Analyzes** with LLM (trends, opportunities, risks)
3. **Evaluates** decisions against policy (confidence thresholds)
4. **Executes** allowed decisions (writes to `~/.brand-os/outputs/`)
5. **Escalates** uncertain decisions (Slack notification)
6. **Logs outcomes** for self-improvement

### Loop Commands

```bash
brandos loop start                    # Start autonomous loop
brandos loop start --brand mycompany  # Single brand only
brandos loop test mycompany           # Test one cycle

brandos decision list                 # View all decisions
brandos decision pending              # Decisions needing review
brandos decision approve <id>         # Approve escalated decision

brandos policy show mycompany         # View policy config
brandos policy test mycompany         # Test policy evaluation

brandos learn metrics mycompany       # View learning metrics
brandos learn recommendations myco    # Get improvement suggestions
```

### Policy Configuration

Control autonomous behavior in `brand.yml`:

```yaml
policy:
  enabled: true
  default_verdict: escalate  # allow, escalate, deny
  global_min_confidence: 0.7

  always_allow:
    - signal_action
  always_escalate:
    - budget_allocation

  rules:
    - name: content-auto-publish
      decision_types: [content_publish]
      min_confidence: 0.8
      max_per_hour: 5
      cooldown_minutes: 10
```

### Requirements

| Component | Required | Notes |
|-----------|----------|-------|
| `GOOGLE_API_KEY` | Yes | For LLM analysis (Gemini) |
| `ANTHROPIC_API_KEY` | Alt | Alternative LLM (Claude) |
| `SLACK_WEBHOOK_URL` | No | For escalation alerts |
| Brand config | Yes | At least one brand in `brands/` |

Without an LLM API key, signals will be fetched but no analysis/decisions will be generated.

## Documentation

| Document | Purpose |
|----------|---------|
| [ROADMAP.md](ROADMAP.md) | Implementation phases from current state to full vision |
| [SIGNAL_STRATEGY.md](SIGNAL_STRATEGY.md) | Signal intelligence positioning and phased build plan |
| [AGENTS.md](AGENTS.md) | Agent architecture and multi-agent coordination |
| [GATEWAY.md](GATEWAY.md) | Gateway coordination layer design |
| [CLAUDE.md](CLAUDE.md) | Development guidelines and conventions |

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
pytest

# Lint
ruff check src/

# Format
ruff format src/
```

## License

MIT
