"""Brand report pipeline using simple callables for aggregation and delivery."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Callable, Iterable, Tuple

from coding_agent.brand.models import BrandReport, BrandSignal


@dataclass(frozen=True)
class BrandTask:
    """Defines the input required to generate a brand report."""

    brand_id: str
    report_date: date
    recipients: Tuple[str, ...]


@dataclass(frozen=True)
class BrandReportToolkit:
    """Collection of pluggable callables for the brand reporting pipeline."""

    gather_signals: Callable[[BrandTask], Iterable[BrandSignal]]
    summarize: Callable[[BrandTask, Tuple[BrandSignal, ...]], BrandReport]
    compose_email: Callable[[BrandTask, BrandReport], Tuple[str, str]]
    send_email: Callable[[BrandTask, str, str], str]
    filter_signals: Callable[[BrandTask, Tuple[BrandSignal, ...]], Tuple[BrandSignal, ...]] | None = None


@dataclass(frozen=True)
class BrandReportResult:
    """Aggregated outputs from a brand reporting run."""

    report: BrandReport
    email_subject: str
    email_body: str
    message_id: str
    signals: Tuple[BrandSignal, ...]


@dataclass
class BrandReportPipeline:
    """Runs the brand reporting workflow using the provided toolkit."""

    toolkit: BrandReportToolkit

    def run(self, task: BrandTask) -> BrandReportResult:
        if not task.recipients:
            raise ValueError("Brand report requires at least one recipient")

        signals_tuple = tuple(self.toolkit.gather_signals(task))
        if self.toolkit.filter_signals is not None:
            signals_tuple = self.toolkit.filter_signals(task, signals_tuple)
        if not signals_tuple:
            raise ValueError("No relevant signals available to summarize")
        report = self.toolkit.summarize(task, signals_tuple)
        subject, body = self.toolkit.compose_email(task, report)
        message_id = self.toolkit.send_email(task, subject, body)

        return BrandReportResult(
            report=report,
            email_subject=subject,
            email_body=body,
            message_id=message_id,
            signals=signals_tuple,
        )
