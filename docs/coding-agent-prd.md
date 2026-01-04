# OpenAI Agents SDK + Temporal Coding Agent PRD

## 0) TL;DR
- Ship a coding copilot that plans, edits, tests, and opens PRs across your repositories.
- Lean on the OpenAI Agents SDK for orchestration, tooling, guardrails, tracing, and multi-agent handoffs.
- Run end-to-end tasks as Temporal Workflows so long, failure-prone execution (clones, builds, tests, human approvals) is durable and horizontally scalable.
- Extend the platform to generate daily brand intelligence reports via email using the same durable runtime and agent cohort.

## 1) Goals (V1)
- Deliver 10 or more merged PRs per week with greater than 70 percent acceptance and fewer than two reviewer cycles per PR.
- Reduce spec-to-PR lead time by 30 percent versus the current baseline.
- Keep the system safe by default: never write directly to default branches and require human approval for merges.
- Operate with fully self-hosted durability by running a Temporal server inside the customer VPC or Kubernetes cluster.

### Non-goals (V1)
- Autonomous merges.
- Cross-organization codebase changes.
- Live production changes without CI.

## 2) Users and top jobs
- Engineer: "Turn this ticket into a clean PR with tests."
- Tech Lead: "Refactor module X and keep the API stable."
- SRE or DevEx: "Upgrade dependency Y across services with safe canaries."

## 3) Core outcomes and metrics
- PR quality: merge rate, regression rate (7 and 30 day), test coverage delta.
- Throughput: PRs per week, time to first PR, time in review.
- Reliability: number of resumed runs after failures via Temporal, cumulative human-in-loop wait time, durable timers enable pauses for hours or days without losing state.
- Safety: count of blocked dangerous operations and guardrail violations caught by Agents SDK guardrails and tracing.
- Brand insights: daily report delivery rate, open rate, accuracy of competitive highlights.

## 4) High-level architecture
[Web/API] --> [Agents Service (Python)]
                |  \
                |   \--(MCP clients)--> [MCP Servers: repo, fs, code-search, runner, http, secrets]
                |
                +--> [Temporal Workflows & Activities] <--> [Temporal Server (OSS, self-hosted)]
                |                                            (Postgres + UI)
                +--> [CI/CD] (GitHub/GitLab Actions)
                +--> [Tracing/Telemetry]

- Agents SDK primitives in play: Agents, Tools, Handoffs, Guardrails, Sessions, Tracing.
- Temporal provides crash-proof execution with retries, timers, and signals and is hosted as OSS inside the customer environment.
- MCP standardizes tools and data interchange, acting as the "USB-C" layer for agents.

## 5) Key workflows (Temporal Workflows)
1. Spec -> Plan -> PR (happy path)
   - Input: ticket link plus acceptance criteria.
   - Activities: Plan (LLM), Fetch context (code search), Edit (apply changes), Build and test, Create PR, Await review (Temporal sleep or signal), Incorporate feedback, Ready to merge (human merges).
   - Each agent invocation runs as an Activity; orchestration logic is a Temporal Workflow.
2. Bug triage and fix
   - Reproduce in sandbox, localize fault, patch, add failing test, open PR.
3. Safe upgrade
   - Plan upgrade, change files across N modules, run targeted tests, open batched PRs.
4. Refactor with guarantees
   - Generate transformation plan, apply minimal diffs, run contract tests, open PR.
5. Daily brand report
   - Schedule a Temporal Cron Workflow per brand.
   - Activities: gather brand and competitor signals (search/MCP/http), synthesize insights, summarize into email-safe Markdown, send via email provider with guardrails around sensitive outputs.
   - Capture delivery metrics and store report artifacts for auditing.

## 6) Functional requirements
- FR1 Task intake: REST and CLI endpoints create tasks with repo, base branch, ticket URL, and constraints.
- FR2 Planning and traceability: Planner agent emits a change plan listing files, functions, tests to add, rationale, and risk notes.
- FR3 Repository operations via MCP: read, search, and edit files; create branches, commits, and PRs through standardized MCP tools and resources.
- FR4 Execution sandbox: builds, tests, and linters run inside ephemeral containers without host filesystem writes.
- FR5 CI integration: trigger CI, fetch results, and iterate automatically until success or a guardrail halts the run.
- FR6 Human-in-loop: Temporal timers and signals wait for review and resume on comment callbacks.
- FR7 Guardrails: restrict writes to allowed paths, enforce "tests changed if code changed," and require green CI before PR completion using Agents SDK guardrails and schema checks.
- FR8 Multi-repo scope: run against a single repo per task in V1 with multi-repo support gated behind a feature flag for V2.
- FR9 Brand reporting: ingest brand signals (news, social, owned channels), synthesize daily email reports, and deliver via transactional email service with tracking.

## 7) Non-functional requirements
- Reliability: recover from crashes or redeploys, keep Activities idempotent, and maintain deterministic Workflow code by keeping side-effectful work in Activities.
- Scale: scale horizontally by adding Workers; dedicate pools per agent if needed because each micro-agent runs as its own Activity.
- Security:
  - Use least-privilege Git tokens with read-only defaults and service-account based PR creation.
  - Pin and verify MCP servers, maintain an allowlist, and block egress by default. Treat third-party MCP servers as untrusted code and audit or lock versions.
- Observability: leverage Agents SDK tracing, the Temporal UI, and OpenTelemetry sinks.
- Self-hosting: deploy the Temporal server (OSS) with Postgres and Web UI on Kubernetes or VMs.

## 8) Agent cohort (Agents SDK)
- PlannerAgent: turns tickets into structured change plans (JSON) with rationale and risk.
- RetrieverAgent: gathers relevant code and docs via MCP repo, code-search, and http tools.
- CoderAgent: applies diffs, writes tests, and respects constraints.
- CriticAgent: performs self-review for side effects, missing tests, or policy violations.
- FixerAgent: incorporates CI or reviewer feedback.
- ReporterAgent: aggregates brand signals, drafts email summaries, and coordinates delivery guardrails.
- Use handoffs between agents to minimize scope per agent and capture every step in tracing.

## 9) Tools (via MCP and native function tools)
- repo: open, read, write, search; create branches, commits, and PRs.
- runner: execute commands in ephemeral containers for lint, build, and test steps.
- code-search: provide semantic and AST search over indexed code.
- http: fetch documentation or changelog references.
- secrets: broker scoped credentials.
- email: transactional email sender with templates, rate limits, and delivery receipts.
- MCP defines Resources (context) and Tools (functions) over JSON-RPC with progress, cancellation, and logging.

## 10) Temporal design
- Workflow: `CodingTaskWorkflow(task_id, repo, base_branch, policy)`
- Activities (idempotent, retryable):
  1. PlanChanges (LLM call via Agents SDK Runner)
  2. FetchContext (search or index lookups)
  3. ApplyDiffs (edit files and commit to feature branch)
  4. RunCI (containerized build and test)
  5. OpenPR (create PR and description)
  6. AwaitReview (sleep with timeout and resume on webhook signal)
  7. AddressFeedback (loop until objectives met or policy stops execution)
- Supplemental Cron Workflow: `BrandReportWorkflow(brand_id, recipients)` running on daily cadence with Activities GatherSignals, SummarizeInsights, ComposeEmail, SendEmail, RecordMetrics.
- Integration note: each agent invocation executes through an Activity while the orchestration remains in the Workflow, delivering durability and scale without custom plumbing.

## 11) Data and schemas
**Change Plan (PlannerAgent output)**

```json
{
  "ticket_id": "ENG-1423",
  "goal": "Add retries to payment client",
  "constraints": ["no API change", "add unit+integration tests"],
  "edits": [
    {"path": "pkg/payments/client.py", "intent": "wrap calls with retry"},
    {"path": "tests/test_payments_client.py", "intent": "add flaky API test"}
  ],
  "risk": ["timeout propagation", "idempotency"],
  "checks": ["lint", "pytest -k payments", "coverage>75%"]
}
```

**PR description (agent composed)**
- What changed.
- Why it changed.
- How to test.
- Rollback plan.
- Links to evidence such as CI runs.

**Brand report (ReporterAgent output)**
```json
{
  "brand_id": "br-42",
  "date": "2025-01-15",
  "highlights": [
    {"title": "Competitor launches loyalty program", "impact": "High", "summary": "..."},
    {"title": "Social sentiment dips 5%", "impact": "Medium", "summary": "..."}
  ],
  "metrics": {
    "share_of_voice": 0.34,
    "sentiment_delta": -0.05
  },
  "actions": ["Review competitor offer", "Launch positive sentiment campaign"]
}
```

## 12) Guardrails and policy
- Enforce write constraints: only allowed paths and no secrets in diffs.
- Require tests to change whenever code changes and block PR completion until CI is green.
- Block dangerous operations (networking, infrastructure scripts) unless a policy flag explicitly allows them.
- Maintain MCP hygiene: version pinning, SLSA provenance when available, internal registry mirrors, and periodic audits in response to recent malicious MCP server incidents.
- Agents SDK guardrails validate inputs and outputs for plans and diffs before allowing progression.
- Email guardrails ensure PII redaction, ban on disallowed topics, and validation of recipient allowlists before send.

## 13) UI (minimal)
- Task detail view: status, current step, logs, planned edits, live CI status.
- PR preview: rendered diff, test results, risk callouts, approve or request changes controls.
- Run timeline: cross-links between Agents SDK traces and the Temporal execution graph.

## 14) Evaluations
- Offline: maintain a golden set of 10 to 20 tickets and measure pass-at-merge and reviewer cycles.
- Online: schedule canary tasks each week and compare lead time versus developer baseline.
- Reliability: inject forced failures and confirm Workflows resume at the last successful step, exercising Temporal durability guarantees.
- Email reporting: track delivery/open metrics, validate content accuracy against curated truth sets.

## 15) Rollout plan (phases)
1. MVP (single repo): implement the Plan -> Edit -> Test -> PR loop on a service with strong test coverage.
2. Generalize: add bug-fix flow, safe upgrades, and basic refactors.
3. Scale and harden: expand to a repo matrix, add caching and artifact storage, and bolster guardrails.

## 16) Integrations and infrastructure
- Git providers: GitHub and GitLab via PAT or app with repo-scoped permissions.
- CI: GitHub Actions or GitLab CI through webhooks and status checks.
- Temporal: OSS server, UI, and Postgres deployed on Kubernetes or VMs.
- Observability: combine Agents SDK tracing, Temporal UI visibility, and OpenTelemetry export.
- Email: transactional provider (e.g., SendGrid, Postmark) or SMTP relay with delivery receipts logged to the run.
- Resend support: MVP can use Resend API for email delivery with API-key guardrails and delivery metrics collection.

## 17) Risks and mitigations
- Third-party MCP servers and supply chain exposure: pin versions, verify sources, audit regularly, block egress, and prefer first-party or self-built servers.
- Flaky CI: apply retry policies, maintain test quarantines, and use targeted test selection.
- Prompt drift: freeze prompts per release and run A/B prompt experiments.
- Workflow non-determinism: keep LLM calls in Activities and ensure Workflow code is pure coordination to satisfy Temporal determinism requirements.

## 18) Acceptance criteria (V1)
- Produces PRs with green CI, passing guardrails, and reviewer checklist compliance.
- Recovers from mid-run failures or redeploys without manual intervention.
- Completes at least feature, bugfix, and small refactor task types end to end.
- Maintains acceptable end-to-end latency: target p95 under 45 minutes for medium tasks; longer work parks on durable timers.

## 19) API sketch (external)
- POST `/tasks` -> start `CodingTaskWorkflow`.
- GET `/tasks/{id}` -> return status, current step, artifacts, Temporal run ID.
- POST `/tasks/{id}/signals/review` -> deliver reviewer feedback and resume execution.
- GET `/prs/{id}` -> return composed PR description and risk notes.

## 20) Build notes (opinionated)
- Run the Agents SDK Runner inside Temporal Activities and keep Workflows thin.
- Maintain one Worker pool for Activities sized for CPU, memory, and build or test runtime.
- Containerize execution, mounting repositories read-only except for the working tree.
- Pre-index code (ctags, tree-sitter, embeddings) for fast, relevant retrieval.
- Store artifacts such as plans, diffs, and logs alongside run metadata.

## Appendix: Optional drafts
- Change Plan Pydantic model that matches the Agents SDK `output_type`.
- `CodingTaskWorkflow` signature with signal and timer definitions.
- Minimal MCP server contracts for repo, runner, and code-search tools.
