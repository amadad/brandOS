"""Signals CLI commands."""
from __future__ import annotations

import typer
from rich.console import Console

from brand_os.cli_utils import emit

signals_app = typer.Typer(help="Signal monitoring commands.")
console = Console()


@signals_app.command("fetch")
def fetch(
    brand: str = typer.Option(..., "--brand", "-b", help="Brand name"),
    source: str = typer.Option("google_news", "--source", "-s", help="Signal source"),
    query: str | None = typer.Option(None, "--query", "-q", help="Custom search query"),
    limit: int = typer.Option(20, "--limit", "-l", help="Max signals to fetch"),
    save: bool = typer.Option(True, "--save/--no-save", help="Save to history"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Fetch signals from a source."""
    from brand_os.core.brands import load_brand_config
    from brand_os.signals.history import append_signals
    from brand_os.signals.providers.google_news import fetch_google_news

    config = load_brand_config(brand)

    # Build query from brand keywords if not provided
    if not query:
        keywords = config.get("keywords", [])
        name = config.get("name", brand)
        query = f"{name} OR " + " OR ".join(keywords[:5]) if keywords else name

    console.print(f"Fetching signals for: {query}")

    if source == "google_news":
        signals = fetch_google_news(query, limit=limit)
    else:
        console.print(f"[red]Unknown source: {source}[/red]")
        raise typer.Exit(1)

    console.print(f"Found {len(signals)} signals")

    if save and signals:
        count = append_signals(brand, signals)
        console.print(f"Saved {count} new signals to history")

    emit(signals, format)


@signals_app.command("filter")
def filter_cmd(
    brand: str = typer.Option(..., "--brand", "-b", help="Brand name"),
    min_score: float = typer.Option(0.1, "--min-score", "-m", help="Minimum relevance score"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Filter signals by relevance."""
    from brand_os.core.brands import load_brand_config
    from brand_os.signals.history import query_signals
    from brand_os.signals.relevance import filter_signals

    config = load_brand_config(brand)

    # Get recent signals
    signals = query_signals(brand, limit=200)
    console.print(f"Loaded {len(signals)} signals from history")

    # Filter by relevance
    filtered = filter_signals(
        signals,
        keywords=config.get("keywords", []),
        competitors=config.get("competitors", []),
        stop_phrases=config.get("stop_phrases", []),
        min_score=min_score,
    )

    console.print(f"Filtered to {len(filtered)} relevant signals")

    emit(filtered, format)


@signals_app.command("history")
def history(
    brand: str = typer.Option(..., "--brand", "-b", help="Brand name"),
    query: str | None = typer.Option(None, "--query", "-q", help="Search query"),
    since: str | None = typer.Option(None, "--since", "-s", help="Date filter (ISO or '7d')"),
    limit: int = typer.Option(50, "--limit", "-l", help="Max results"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Query signal history."""
    from brand_os.signals.history import get_signal_count, query_signals

    total = get_signal_count(brand)
    console.print(f"Total signals in history: {total}")

    signals = query_signals(brand, query=query, since=since, limit=limit)
    console.print(f"Returning {len(signals)} signals")

    emit(signals, format)
