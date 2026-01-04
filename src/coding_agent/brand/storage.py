"""Persistent storage helpers for brand reporting."""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import date
from pathlib import Path
from typing import Iterable

import kuzu

from coding_agent.brand.models import BrandReport, BrandSignal

logger = logging.getLogger(__name__)

DATA_ROOT = Path(os.environ.get("BRANDOS_DATA_ROOT", "data/reports"))
KUZU_PATH = Path(os.environ.get("BRANDOS_KUZU_PATH", "data/kuzu/brandos.db"))

# Pattern for valid brand IDs: alphanumeric, hyphens, underscores only
_BRAND_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def _sanitize_brand_id(brand_id: str) -> str:
    """Validate brand_id to prevent path traversal attacks."""
    if not brand_id:
        raise ValueError("brand_id must not be empty")
    if not _BRAND_ID_PATTERN.match(brand_id):
        raise ValueError("brand_id must contain only alphanumeric characters, hyphens, and underscores")
    return brand_id


def _escape(value: str | None) -> str:
    if value is None:
        return ""
    return value.replace("'", "''")


def persist_raw_signals(brand_id: str, report_date: date, signals: Iterable[BrandSignal]) -> Path:
    brand_id = _sanitize_brand_id(brand_id)
    folder = DATA_ROOT / brand_id / report_date.isoformat()
    folder.mkdir(parents=True, exist_ok=True)
    payload = [signal.model_dump(mode="json") for signal in signals]
    output = folder / "signals.json"
    with output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return output


def persist_report_summary(brand_id: str, report: BrandReport, message_id: str) -> Path:
    brand_id = _sanitize_brand_id(brand_id)
    folder = DATA_ROOT / brand_id / report.report_date.isoformat()
    folder.mkdir(parents=True, exist_ok=True)
    payload = {
        "report": report.model_dump(mode="json"),
        "message_id": message_id,
    }
    output = folder / "summary.json"
    with output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return output


def _get_connection() -> kuzu.Connection:
    KUZU_PATH.parent.mkdir(parents=True, exist_ok=True)
    database = kuzu.Database(str(KUZU_PATH))
    return kuzu.Connection(database)


def _ensure_schema(conn: kuzu.Connection) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS Brand(id STRING, name STRING, PRIMARY KEY(id));"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS Report(id STRING, brand_id STRING, report_date STRING, overview STRING, metrics STRING, message_id STRING, PRIMARY KEY(id));"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS Highlight(id STRING, report_id STRING, headline STRING, impact STRING, source STRING, summary STRING, url STRING, PRIMARY KEY(id));"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS BrandReports(brand_id STRING, report_id STRING, created_at STRING);"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS ReportHighlights(report_id STRING, highlight_id STRING);"
    )


def persist_to_kuzu(brand_id: str, report: BrandReport, message_id: str, signals: Iterable[BrandSignal]) -> None:
    brand_id = _sanitize_brand_id(brand_id)
    try:
        conn = _get_connection()
        _ensure_schema(conn)
    except Exception as error:  # pragma: no cover - environment specific
        logger.warning("Skipping Kùzu persistence: %s", error)
        return

    brand_node_id = _escape(brand_id)
    brand_name = _escape(brand_id.title())
    try:
        conn.execute(f"INSERT INTO Brand(id, name) VALUES ('{brand_node_id}', '{brand_name}')")
    except Exception as error:
        logger.debug("Brand insert skipped (likely exists): %s", error)

    report_id = _escape(f"{brand_id}:{report.report_date.isoformat()}:{message_id}")
    overview = _escape(report.overview or "")
    metrics_json = _escape(json.dumps(report.metrics, sort_keys=True))
    message = _escape(message_id)
    report_date_str = _escape(report.report_date.isoformat())

    try:
        conn.execute(
            "INSERT INTO Report(id, brand_id, report_date, overview, metrics, message_id) "
            f"VALUES ('{report_id}', '{brand_node_id}', '{report_date_str}', '{overview}', '{metrics_json}', '{message}')"
        )
    except Exception as error:  # pragma: no cover - duplicates handled by skipping
        logger.debug("Report insert skipped: %s", error)
        return

    try:
        conn.execute(
            f"INSERT INTO BrandReports(brand_id, report_id, created_at) VALUES ('{brand_node_id}', '{report_id}', '{report_date_str}')"
        )
    except Exception as error:
        logger.debug("BrandReports edge insert skipped: %s", error)

    for index, signal in enumerate(signals):
        highlight_id = _escape(f"{report_id}:{index}")
        headline = _escape(signal.headline)
        impact = _escape(signal.impact)
        source = _escape(signal.source)
        summary = _escape(signal.summary or "")
        url = _escape(signal.url or "")

        try:
            conn.execute(
                "INSERT INTO Highlight(id, report_id, headline, impact, source, summary, url) "
                f"VALUES ('{highlight_id}', '{report_id}', '{headline}', '{impact}', '{source}', '{summary}', '{url}')"
            )
            conn.execute(
                f"INSERT INTO ReportHighlights(report_id, highlight_id) VALUES ('{report_id}', '{highlight_id}')"
            )
        except Exception as error:
            logger.debug("Highlight insert skipped for %s: %s", highlight_id, error)
            continue
