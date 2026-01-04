from datetime import date
from typing import List

import pytest

from coding_agent.brand.models import BrandReport, BrandSignal
from coding_agent.brand.pipeline import (
    BrandReportPipeline,
    BrandReportResult,
    BrandReportToolkit,
    BrandTask,
)


def test_pipeline_generates_report_and_email():
    signals: List[BrandSignal] = [
        BrandSignal(source="news", headline="Competitor launches loyalty program", impact="high"),
        BrandSignal(source="social", headline="Sentiment dips", impact="medium"),
    ]

    toolkit = BrandReportToolkit(
        gather_signals=lambda task: signals,
        filter_signals=lambda task, sigs: tuple(sigs),
        summarize=lambda task, signals: BrandReport(
            brand_id=task.brand_id,
            report_date=task.report_date,
            highlights=tuple(signals),
            metrics={"total_signals": 2},
            actions=("Review competitor offer", "Monitor sentiment"),
            overview="Competitor launches loyalty program; sentiment dip observed.",
            risks=("Limited signal volume",),
        ),
        compose_email=lambda task, report: (
            f"Daily brand report for {task.brand_id}",
            "Summary: 2 highlights",
        ),
        send_email=lambda task, subject, body: "msg-123",
    )

    pipeline = BrandReportPipeline(toolkit=toolkit)
    result = pipeline.run(BrandTask(brand_id="br-42", report_date=date(2025, 1, 15), recipients=("ops@example.com",)))

    assert isinstance(result, BrandReportResult)
    assert result.report.metrics["total_signals"] == 2
    assert result.report.overview is not None
    assert result.email_subject.startswith("Daily brand report")
    assert result.message_id == "msg-123"
    assert len(result.signals) == 2


def test_pipeline_requires_recipients():
    pipeline = BrandReportPipeline(
        toolkit=BrandReportToolkit(
            gather_signals=lambda task: [],
            filter_signals=lambda task, sigs: tuple(sigs),
            summarize=lambda task, signals: BrandReport(
                brand_id=task.brand_id,
                report_date=task.report_date,
                highlights=(),
                metrics={},
                actions=(),
            ),
            compose_email=lambda task, report: ("subject", "body"),
            send_email=lambda task, subject, body: "msg-1",
        )
    )

    with pytest.raises(ValueError):
        pipeline.run(BrandTask(brand_id="br-1", report_date=date.today(), recipients=()))
