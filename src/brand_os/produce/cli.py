"""Produce CLI commands."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from brand_os.cli_utils import emit

produce_app = typer.Typer(help="Content production commands.")
console = Console()


@produce_app.command("copy")
def copy_cmd(
    topic: str = typer.Argument(..., help="Content topic"),
    brand: str | None = typer.Option(None, "--brand", "-b", help="Brand name"),
    platform: str = typer.Option("twitter", "--platform", "-p", help="Target platform"),
    eval: bool = typer.Option(False, "--eval", help="Evaluate content quality"),
    heal: bool = typer.Option(False, "--heal", help="Auto-heal content if eval fails"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Generate copy for a platform."""
    from brand_os.core.brands import load_brand_config
    from brand_os.produce.copy import generate_copy, produce_and_eval

    voice = None
    hooks = None

    if brand:
        try:
            config = load_brand_config(brand)
            voice = config.get("voice")

            # Load hooks if available
            import json

            from brand_os.core.brands import get_brand_intel_dir

            hooks_file = get_brand_intel_dir(brand) / "hooks.json"
            if hooks_file.exists():
                hooks = json.loads(hooks_file.read_text())[:5]
        except ValueError:
            pass

    eval = eval or heal

    if eval or heal:
        result = produce_and_eval(
            topic=topic,
            brand=brand,
            platform=platform,
            voice=voice,
            hooks=hooks,
            eval=eval,
            heal=heal,
        )
    else:
        result = generate_copy(
            topic=topic,
            brand=brand,
            platform=platform,
            voice=voice,
            hooks=hooks,
        )

    if format == "text":
        _render_copy_text(result)
        return

    emit(result, format)


def _render_copy_text(result: dict) -> None:
    """Render `produce copy` output in human-readable text mode."""
    main = result.get("main", "")
    variants = result.get("variants", [])
    hashtags = result.get("hashtags", [])

    console.print("[bold]Main[/bold]")
    console.print(main)

    if variants:
        console.print("\n[bold]Variants[/bold]")
        for idx, variant in enumerate(variants, 1):
            console.print(f"{idx}. {variant}")

    if hashtags:
        console.print("\n[bold]Hashtags[/bold]")
        console.print(" ".join(hashtags))

    eval_result = result.get("eval")
    if not isinstance(eval_result, dict):
        return

    console.print()
    table = Table(title="Eval Scores")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Score", f"{eval_result.get('score', 0.0):.2f}")
    passed = bool(eval_result.get("passed", False))
    table.add_row("Passed", "[green]Yes[/green]" if passed else "[red]No[/red]")

    if "original_score" in result:
        table.add_row("Original Score", f"{result.get('original_score', 0.0):.2f}")
    if "healed" in result:
        table.add_row("Healed", "Yes" if result.get("healed") else "No")
    if "heal_iterations" in result:
        table.add_row("Heal Iterations", str(result.get("heal_iterations", 0)))

    console.print(table)

    dimension_scores = eval_result.get("dimension_scores", [])
    if isinstance(dimension_scores, list) and dimension_scores:
        dim_table = Table(title="Dimension Scores")
        dim_table.add_column("Dimension")
        dim_table.add_column("Score")
        dim_table.add_column("Passed")
        for dim in dimension_scores:
            if not isinstance(dim, dict):
                continue
            dim_passed = bool(dim.get("passed", False))
            dim_table.add_row(
                str(dim.get("name", "")),
                f"{dim.get('score', 0.0):.2f}",
                "[green]Yes[/green]" if dim_passed else "[red]No[/red]",
            )
        console.print(dim_table)


@produce_app.command("thread")
def thread_cmd(
    topic: str = typer.Argument(..., help="Thread topic"),
    brand: str | None = typer.Option(None, "--brand", "-b", help="Brand name"),
    tweets: int = typer.Option(5, "--tweets", "-n", help="Number of tweets"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Generate a Twitter/X thread."""
    from brand_os.produce.copy import generate_thread

    result = generate_thread(topic=topic, brand=brand, num_tweets=tweets)

    if format == "text":
        for i, tweet in enumerate(result, 1):
            console.print(f"[bold]{i}/[/bold] {tweet}")
            console.print()
    else:
        emit({"tweets": result}, format)


@produce_app.command("image")
def image_cmd(
    direction: str = typer.Argument(..., help="Image direction/prompt"),
    brand: str | None = typer.Option(None, "--brand", "-b", help="Brand name"),
    style: Path | None = typer.Option(None, "--style", "-s", help="Style reference image"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output path"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Generate an image."""
    from brand_os.produce.image import generate_image

    result = generate_image(
        direction=direction,
        brand=brand,
        style_ref=style,
        output_path=output,
    )

    emit(result, format)


@produce_app.command("video")
def video_cmd(
    brief: str = typer.Argument(..., help="Video brief"),
    brand: str | None = typer.Option(None, "--brand", "-b", help="Brand name"),
    duration: int = typer.Option(30, "--duration", "-d", help="Duration in seconds"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Generate a video (experimental)."""
    from brand_os.produce.video import generate_video

    result = generate_video(brief=brief, brand=brand, duration=duration)

    emit(result, format)


@produce_app.command("explore")
def explore_cmd(
    topic: str = typer.Argument(..., help="Topic to explore"),
    brand: str = typer.Option(..., "--brand", "-b", help="Brand name"),
    platforms: str = typer.Option(
        "twitter,linkedin", "--platforms", "-p", help="Platforms (comma-separated)"
    ),
    heal: bool = typer.Option(False, "--heal", help="Auto-heal content if eval fails"),
    add_to_queue: bool = typer.Option(True, "--queue/--no-queue", help="Add to queue"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Full exploration flow: generate copy for multiple platforms and optionally queue."""
    import json

    from brand_os.core.brands import get_brand_intel_dir, load_brand_config
    from brand_os.produce.copy import produce_and_eval
    from brand_os.produce.queue import enqueue

    config = load_brand_config(brand)
    voice = config.get("voice")

    # Load hooks
    hooks = None
    hooks_file = get_brand_intel_dir(brand) / "hooks.json"
    if hooks_file.exists():
        hooks = json.loads(hooks_file.read_text())[:5]

    # Load learnings
    learnings = None
    learnings_file = get_brand_intel_dir(brand).parent / "learnings.json"
    if learnings_file.exists():
        learnings_data = json.loads(learnings_file.read_text())
        learnings = learnings_data.get("suggestions", [])[:5]

    platform_list = [p.strip() for p in platforms.split(",")]
    results = []

    for platform in platform_list:
        console.print(f"Generating {platform} content...")

        result = produce_and_eval(
            topic=topic,
            brand=brand,
            platform=platform,
            voice=voice,
            hooks=hooks,
            learnings=learnings,
            eval=True,
            heal=heal,
        )

        results.append({"platform": platform, **result})

        if add_to_queue and result.get("main"):
            eval_result = result.get("eval", {})
            score = eval_result.get("score") if isinstance(eval_result, dict) else None
            passed = (
                bool(eval_result.get("passed", False)) if isinstance(eval_result, dict) else False
            )
            enqueue(
                brand,
                result["main"],
                platform=platform,
                metadata={"eval_score": score, "eval_passed": passed},
            )
            console.print("  Added to queue")
            if not passed:
                score_text = f"{score:.2f}" if isinstance(score, (int, float)) else "n/a"
                console.print(
                    f"  [yellow]WARNING:[/yellow] Queued content failed eval (score: {score_text})"
                )

    emit(results, format)
