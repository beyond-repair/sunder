#!/usr/bin/env python3
"""python -m sunder \"your goal\""""
from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from sunder.agent import Agent

console = Console()

@click.command()
@click.argument("goal", required=False)
@click.option("--workspace", "-w", default=".", help="Project root to operate on")
@click.option("--max-steps", default=12, show_default=True)
@click.option("--offline/--online", default=True, help="Offline mode (default)")
def main(goal: str | None, workspace: str, max_steps: int, offline: bool):
    """SUNDER — SCAN → SNAP → SUNDER"""
    console.print(Panel.fit(
        "[bold magenta]SUNDER[/]  ·  local-first autonomous coding agent\n"
        "[dim]THE CITY WRITES ITS OWN REALITY. YOU JUST EDIT IT.[/]",
        border_style="magenta",
    ))

    if not goal:
        console.print("[yellow]Usage:[/] python -m sunder \"Refactor auth and add tests\"")
        sys.exit(0)

    root = Path(workspace).resolve()
    agent = Agent(workspace=root, offline=offline, max_steps=max_steps)
    result = agent.run(goal)

    console.print()
    console.print(Panel(
        f"[bold]Status:[/] {result['status']}\n"
        f"[bold]Steps:[/] {result['steps']}\n"
        f"[bold]Forks created:[/] {result.get('forks', 0)}",
        title="SUNDER RESULT",
        border_style="cyan",
    ))

if __name__ == "__main__":
    main()
