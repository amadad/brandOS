"""CLI demos for coding and brand-report workflows."""

from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import requests
from dotenv import load_dotenv

from coding_agent.brand import (
    BrandReport,
    BrandReportPipeline,
    BrandReportToolkit,
    BrandSignal,
    BrandTask,
    HeuristicSummarizer,
    InMemoryEmailSender,
    FileSignalsProvider,
    StaticSignalsProvider,
    WebPageSignalsProvider,
    GoogleNewsProvider,
    build_resend_from_env,
    get_brand_profile,
    apply_relevance_filter,
)
from coding_agent.brand.storage import (
    persist_raw_signals,
    persist_report_summary,
    persist_to_kuzu,
)
from coding_agent.adapters import (
    AgentsToolkitFactory,
    CoderAgentAdapter,
    PlannerAgentAdapter,
    PullRequestAdapter,
    RetrieverAgentAdapter,
    ReviewAdapter,
    RunnerAdapter,
    TemporalAwaiter,
)
from coding_agent.adapters.temporal import ReviewSignalGateway
from coding_agent.models import ChangePlan
from coding_agent.orchestrator import CIResult, ReviewResult, TaskInput
from coding_agent.runtime import CodingAgentRuntime, ExecutionObserver

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = PROJECT_ROOT / "docs" / "sample_signals"

GENERIC_FALLBACK_SIGNAL = BrandSignal(
    source="fallback",
    headline="No verified signals available",
    impact="low",
    summary="Automated collectors returned no relevant updates; manual review recommended.",
)


class PrintObserver(ExecutionObserver):
    """Observer that prints each step to stdout."""

    def on_step(self, step: str, payload: Dict[str, Any]) -> None:
        details = ", ".join(f"{key}={value}" for key, value in payload.items() if value is not None)
        print(f"{step}: {details}")


class InlineReviewGateway(ReviewSignalGateway):
    """Minimal gateway that approves instantly for the demo CLI."""

    def wait_for_review(self, task: TaskInput, pr_url: str) -> ReviewResult:
        return ReviewResult(approved=True)


def _load_sample_signals(brand_id: str) -> Tuple[BrandSignal, ...]:
    brand_specific = SAMPLE_DIR / f"{brand_id}.json"
    if brand_specific.exists():
        return tuple(FileSignalsProvider(path=brand_specific).load(brand_id))

    default_path = SAMPLE_DIR / "default.json"
    if default_path.exists():
        return tuple(FileSignalsProvider(path=default_path).load(brand_id))

    return (GENERIC_FALLBACK_SIGNAL,)


def _default_signals_provider(
    brand_id: str,
    signals_file: Path | None,
    brand_url: str | None,
) -> Iterable[BrandSignal]:
    if signals_file and signals_file.exists():
        provider = FileSignalsProvider(path=signals_file)
        return provider.load(brand_id)

    if brand_url:
        provider = WebPageSignalsProvider(url=brand_url)
        try:
            signals = tuple(provider.load(brand_id))
            if signals:
                return signals
        except requests.RequestException as error:
            logger.warning("Web provider failed for %s: %s", brand_url, error)

    try:
        news_provider = GoogleNewsProvider(query=f"{brand_id} brand")
        news_signals = tuple(news_provider.load(brand_id))
        if news_signals:
            return news_signals
    except requests.RequestException as error:
        logger.warning("Google News provider failed for %s: %s", brand_id, error)

    sample_signals = _load_sample_signals(brand_id)
    return StaticSignalsProvider(sample_signals).load(brand_id)


def _compose_plaintext_email(task: BrandTask, report: BrandReport) -> Tuple[str, str]:
    top_highlight = report.highlights[0].headline if report.highlights else "Latest update"
    subject = f"Daily BrandOS Report — {report.report_date.isoformat()} — {top_highlight}"

    body_lines = [
        f"Brand: {task.brand_id}",
        f"Date: {report.report_date.isoformat()}",
        "",
        "Overview:",
        report.overview or "No major shifts detected in the last sampling window.",
        "",
        "Highlights:",
    ]
    for signal in report.highlights:
        body_lines.append(f"- [{signal.source}] {signal.headline} ({signal.impact})")
        if signal.summary:
            body_lines.append(f"  {signal.summary}")

    body_lines.append("")
    body_lines.append("Metrics:")
    if report.metrics:
        for key, value in report.metrics.items():
            body_lines.append(f"- {key.replace('_', ' ').title()}: {value}")
    else:
        body_lines.append("- No metrics captured.")

    body_lines.append("")
    body_lines.append("Recommended Actions:")
    for action in report.actions:
        body_lines.append(f"- {action}")

    if report.risks:
        body_lines.append("")
        body_lines.append("Risks & Watchlist:")
        for risk in report.risks:
            body_lines.append(f"- {risk}")

    return subject, "\n".join(body_lines)


def run_brand_report_demo(
    brand_id: str = "brandos",
    signals_file: Path | None = None,
    brand_url: str | None = None,
    send_via_resend: bool = False,
    resend_sender: str | None = None,
    recipients: Tuple[str, ...] | None = None,
) -> str:
    """Run the brand report pipeline with configurable inputs."""

    def gather_signals(task: BrandTask):
        print("GatherSignals: collecting brand intelligence")
        return tuple(_default_signals_provider(task.brand_id, signals_file, brand_url))

    def filter_signals(task: BrandTask, signals: tuple[BrandSignal, ...]) -> tuple[BrandSignal, ...]:
        profile = get_brand_profile(task.brand_id)
        filtered, rejected = apply_relevance_filter(signals, profile)
        for entry in rejected:
            logger.info("Rejected '%s': %s", entry.signal.headline, entry.reason)
        if filtered:
            return filtered
        logger.warning("All signals rejected for %s; falling back to curated samples", task.brand_id)
        fallback_signals = _load_sample_signals(task.brand_id)
        return tuple(fallback_signals)

    summarizer = HeuristicSummarizer()

    def summarize(task: BrandTask, signals: tuple[BrandSignal, ...]) -> BrandReport:
        print(f"SummarizeInsights: {len(signals)} signals")
        return summarizer.summarize(task.brand_id, task.report_date, signals)

    def compose_email(task: BrandTask, report: BrandReport) -> tuple[str, str]:
        print("ComposeEmail: generating digest")
        return _compose_plaintext_email(task, report)

    if send_via_resend:
        email_sender = build_resend_from_env(resend_sender)
    else:
        email_sender = InMemoryEmailSender()

    def send_email(task: BrandTask, subject: str, body: str) -> str:
        print(f"SendEmail: to={','.join(task.recipients)} subject='{subject}'")
        return email_sender.send(task, subject, body)

    pipeline = BrandReportPipeline(
        toolkit=BrandReportToolkit(
            gather_signals=gather_signals,
            filter_signals=filter_signals,
            summarize=summarize,
            compose_email=compose_email,
            send_email=send_email,
        )
    )

    result = pipeline.run(
        BrandTask(
            brand_id=brand_id,
            report_date=date.today(),
            recipients=recipients or ("brand-team@example.com",),
        )
    )

    persist_raw_signals(brand_id, result.report.report_date, result.signals)
    persist_report_summary(brand_id, result.report, result.message_id)
    persist_to_kuzu(brand_id, result.report, result.message_id, result.signals)

    print("BrandReport: ready for delivery")
    return result.message_id


def _demo_plan() -> ChangePlan:
    return ChangePlan.model_validate(
        {
            "ticket_id": "ENG-1423",
            "goal": "Add retries to payment client",
            "constraints": ["no API change", "add unit tests"],
            "edits": [
                {"path": "pkg/payments/client.py", "intent": "wrap calls with retry"},
                {"path": "tests/test_payments_client.py", "intent": "add flaky API test"},
            ],
            "risk": ["timeout propagation", "idempotency"],
            "checks": ["pytest -k payments", "lint"],
        }
    )


def run_demo_task() -> str:
    """Run the orchestrator with demo adapters and surface the PR URL."""

    factory = AgentsToolkitFactory(
        planner=PlannerAgentAdapter(lambda task: _demo_plan()),
        retriever=RetrieverAgentAdapter(lambda task, plan: {"files": [edit.path for edit in plan.edits]}),
        coder=CoderAgentAdapter(lambda task, plan, context: "demo-commit-sha"),
        runner=RunnerAdapter(lambda task, plan, commit: CIResult(passed=True, url="https://ci.example/jobs/123")),
        pull_requests=PullRequestAdapter(lambda task, plan, commit, ci: f"https://git.example/{task.ticket_id}/pull/1"),
        reviewers=ReviewAdapter(
            await_review=TemporalAwaiter(gateway=InlineReviewGateway()).await_review,
        ),
    )

    toolkit = factory.build()
    runtime = CodingAgentRuntime(toolkit=toolkit, observer=PrintObserver())
    result = runtime.execute(
        TaskInput(ticket_id="ENG-1423", repository="git@example/repo", base_branch="main")
    )
    print(f"PR ready at {result.pr_url}")
    return result.pr_url


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Coding agent demos")
    parser.add_argument("--pipeline", choices=("coding", "brand"), default="coding")
    parser.add_argument("--brand", default="brandos", help="Brand identifier for reporting")
    parser.add_argument("--signals-file", type=Path, help="Path to JSON signals file")
    parser.add_argument("--brand-url", help="Fetch highlights from this brand URL")
    parser.add_argument(
        "--send-resend",
        action="store_true",
        help="Send the brand email via Resend (requires RESEND_API_KEY)",
    )
    parser.add_argument(
        "--resend-from",
        help="Override the Resend sender address (defaults to RESEND_FROM_ADDRESS)",
    )
    parser.add_argument(
        "--recipients",
        help="Comma-separated list of email recipients for the brand report",
    )

    args = parser.parse_args()

    if args.pipeline == "brand":
        run_brand_report_demo(
            brand_id=args.brand,
            signals_file=args.signals_file,
            brand_url=args.brand_url,
            send_via_resend=args.send_resend,
            resend_sender=args.resend_from,
            recipients=tuple(email.strip() for email in args.recipients.split(",")) if args.recipients else None,
        )
    else:
        run_demo_task()


if __name__ == "__main__":  # pragma: no cover
    main()
