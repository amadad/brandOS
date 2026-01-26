"""Plan CLI commands."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from brand_os.cli_utils import emit

plan_app = typer.Typer(help="Campaign planning commands.")
console = Console()


@plan_app.command("research")
def research_cmd(
    brief: str = typer.Argument(..., help="Campaign brief or research question"),
    brand: str | None = typer.Option(None, "--brand", "-b", help="Brand name"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Execute research stage."""
    from brand_os.plan.stages.research import research

    result = research(brief=brief, brand=brand)
    emit(result.model_dump(), format)


@plan_app.command("strategy")
def strategy_cmd(
    input_file: Path | None = typer.Option(None, "--input", "-i", help="Research result JSON"),
    brief: str | None = typer.Option(None, "--brief", help="Brief if no input"),
    brand: str | None = typer.Option(None, "--brand", "-b", help="Brand name"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Execute strategy stage."""
    from brand_os.plan.stages.strategy import strategy

    # Read from file, stdin, or use brief
    research_result = None
    if input_file:
        research_result = json.loads(input_file.read_text())
    elif not sys.stdin.isatty():
        research_result = json.load(sys.stdin)

    result = strategy(research_result=research_result, brief=brief, brand=brand)
    emit(result.model_dump(), format)


@plan_app.command("creative")
def creative_cmd(
    input_file: Path | None = typer.Option(None, "--input", "-i", help="Strategy result JSON"),
    brief: str | None = typer.Option(None, "--brief", help="Brief if no input"),
    brand: str | None = typer.Option(None, "--brand", "-b", help="Brand name"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Execute creative stage."""
    from brand_os.plan.stages.creative import creative

    strategy_result = None
    if input_file:
        strategy_result = json.loads(input_file.read_text())
    elif not sys.stdin.isatty():
        strategy_result = json.load(sys.stdin)

    result = creative(strategy_result=strategy_result, brief=brief, brand=brand)
    emit(result.model_dump(), format)


@plan_app.command("activation")
def activation_cmd(
    input_file: Path | None = typer.Option(None, "--input", "-i", help="Creative result JSON"),
    brief: str | None = typer.Option(None, "--brief", help="Brief if no input"),
    brand: str | None = typer.Option(None, "--brand", "-b", help="Brand name"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Execute activation stage."""
    from brand_os.plan.stages.activation import activation

    creative_result = None
    if input_file:
        creative_result = json.loads(input_file.read_text())
    elif not sys.stdin.isatty():
        creative_result = json.load(sys.stdin)

    result = activation(creative_result=creative_result, brief=brief, brand=brand)
    emit(result.model_dump(), format)


@plan_app.command("run")
def run(
    brief: str = typer.Argument(..., help="Campaign brief"),
    brand: str | None = typer.Option(None, "--brand", "-b", help="Brand name"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Enable human gates"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Run full campaign planning pipeline."""
    from brand_os.plan.stages.research import research
    from brand_os.plan.stages.strategy import strategy
    from brand_os.plan.stages.creative import creative
    from brand_os.plan.stages.activation import activation
    from brand_os.plan.store import save_campaign

    console.print(f"[bold]Starting campaign pipeline[/bold]")
    console.print(f"Brief: {brief[:100]}...")

    # Research
    console.print("\n[bold cyan]Stage 1: Research[/bold cyan]")
    research_result = research(brief=brief, brand=brand)
    console.print(f"  Found {len(research_result.insights)} insights, {len(research_result.competitors)} competitors")

    if interactive:
        if not typer.confirm("Continue to strategy?"):
            raise typer.Abort()

    # Strategy
    console.print("\n[bold cyan]Stage 2: Strategy[/bold cyan]")
    strategy_result = strategy(research_result=research_result.model_dump(), brand=brand)
    console.print(f"  Positioning: {strategy_result.positioning[:80]}...")

    if interactive:
        if not typer.confirm("Continue to creative?"):
            raise typer.Abort()

    # Creative
    console.print("\n[bold cyan]Stage 3: Creative[/bold cyan]")
    creative_result = creative(strategy_result=strategy_result.model_dump(), brand=brand)
    console.print(f"  Generated {len(creative_result.headlines)} headlines, {len(creative_result.ctas)} CTAs")

    if interactive:
        if not typer.confirm("Continue to activation?"):
            raise typer.Abort()

    # Activation
    console.print("\n[bold cyan]Stage 4: Activation[/bold cyan]")
    activation_result = activation(creative_result=creative_result.model_dump(), brand=brand)
    console.print(f"  Planned {len(activation_result.channels)} channels, {len(activation_result.calendar)} calendar items")

    # Compile results
    full_result = {
        "brief": brief,
        "brand": brand,
        "research": research_result.model_dump(),
        "strategy": strategy_result.model_dump(),
        "creative": creative_result.model_dump(),
        "activation": activation_result.model_dump(),
    }

    # Save campaign
    campaign_id = save_campaign(
        brief=brief,
        brand=brand,
        stages=full_result,
    )
    console.print(f"\n[green]Campaign saved: {campaign_id}[/green]")

    # Output
    if output:
        output.write_text(json.dumps(full_result, indent=2, ensure_ascii=False))
        console.print(f"Results saved to: {output}")
    else:
        emit(full_result, format)


@plan_app.command("list")
def list_cmd(
    format: str = typer.Option("table", "--format", "-f", help="Output format"),
) -> None:
    """List saved campaigns."""
    from brand_os.plan.store import list_campaigns

    campaigns = list_campaigns()

    if format == "table":
        table = Table(title="Campaigns")
        table.add_column("ID")
        table.add_column("Brief")
        table.add_column("Brand")
        table.add_column("Stages")
        table.add_column("Created")

        for c in campaigns:
            table.add_row(
                c["id"],
                c["brief"][:40] + "..." if len(c.get("brief", "")) > 40 else c.get("brief", ""),
                c.get("brand") or "",
                ", ".join(c.get("stages", [])),
                c.get("created_at", "")[:10],
            )
        console.print(table)
    else:
        emit(campaigns, format)


@plan_app.command("resume")
def resume(
    campaign_id: str = typer.Argument(..., help="Campaign ID to resume"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Resume a saved campaign."""
    from brand_os.plan.store import load_campaign

    campaign = load_campaign(campaign_id)
    console.print(f"[bold]Loaded campaign: {campaign_id}[/bold]")
    console.print(f"Brief: {campaign.get('brief', '')[:100]}")
    console.print(f"Completed stages: {list(campaign.get('stages', {}).keys())}")

    emit(campaign, format)
