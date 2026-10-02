#!/usr/bin/env python3
"""python -m sunder \"your goal\"

v0.1 heuristic. No supervisor model. --demo runs a corpus task in a scratch
directory under the chosen workspace and does not edit this repository.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from sunder.agent import Agent
from sunder.tasks import SYNTAX_SEED, TASKS

console = Console()


def _prepare_demo_workspace(workspace: Path, demo: str) -> Path:
    root = (workspace / ".sunder" / "demo" / demo).resolve()
    root.mkdir(parents=True, exist_ok=True)
    if demo == "T-003":
        readme = root / "README.md"
        if not readme.exists():
            readme.write_text("LOCAL ONLY\n", encoding="utf-8")
    if demo == "T-004":
        agent_py = root / "sunder" / "agent.py"
        agent_py.parent.mkdir(parents=True, exist_ok=True)
        if not agent_py.exists():
            agent_py.write_text(SYNTAX_SEED, encoding="utf-8")
    return root


@click.command()
@click.argument("goal", required=False)
@click.option("--workspace", "-w", default=".", help="Project root to operate on")
@click.option("--max-steps", default=12, show_default=True, help="Stop the heuristic after this many tool steps")
@click.option("--offline/--online", default=True, help="Offline flag. Network tools stay refused either way in v0.1.")
@click.option(
    "--demo",
    type=click.Choice(sorted(TASKS)),
    default=None,
    help="Run a benchmark heuristic in <workspace>/.sunder/demo/<id>/",
)
def main(goal: str | None, workspace: str, max_steps: int, offline: bool, demo: str | None):
    """SUNDER — SCAN → SNAP → SUNDER (local heuristic, no supervisor LLM)."""
    console.print(Panel.fit(
        "[bold magenta]SUNDER[/]  ·  local-first coding-agent sketch\n"
        "[dim]No supervisor model. SCAN, SNAP, gate, and version-fork only.[/]",
        border_style="magenta",
    ))

    task_id = demo
    if demo:
        goal = TASKS[demo]["prompt"]
        root = _prepare_demo_workspace(Path(workspace), demo)
        console.print(f"[dim]demo workspace[/] {root}")
    else:
        root = Path(workspace).resolve()

    if not goal:
        console.print("[yellow]Usage:[/] python -m sunder \"Inspect this project\"")
        console.print("[yellow]Demo:[/]  python -m sunder --demo T-001")
        sys.exit(0)

    agent = Agent(workspace=root, offline=offline, max_steps=max_steps)
    result = agent.run(goal, task_id=task_id)

    pytest_exit = None
    if demo == "T-001" and result.get("task_met"):
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "tests/test_utils.py", "--tb=short"],
            cwd=root,
            check=False,
        )
        pytest_exit = proc.returncode
        result["pytest_exit"] = pytest_exit
        result["task_met"] = pytest_exit == 0
        if pytest_exit != 0:
            result["note"] = "files were written but pytest failed"
            result["status"] = "FAIL"

    console.print()
    lines = [
        f"[bold]Status:[/] {result['status']}",
        f"[bold]Steps:[/] {result['steps']}",
        f"[bold]Forks created:[/] {result.get('forks', 0)}",
    ]
    if result.get("task_id"):
        lines.append(f"[bold]Task:[/] {result['task_id']} met={result.get('task_met')}")
    if result.get("note"):
        lines.append(f"[bold]Note:[/] {result['note']}")
    if pytest_exit is not None:
        lines.append(f"[bold]pytest:[/] exit {pytest_exit}")
    lines.append(f"[bold]Workspace:[/] {root}")
    console.print(Panel("\n".join(lines), title="SUNDER RESULT", border_style="cyan"))

    if result.get("status") != "OK":
        sys.exit(1)
    if result.get("blocked_source_tree"):
        sys.exit(4)
    if result.get("task_met") is False:
        sys.exit(3)
    sys.exit(0)


if __name__ == "__main__":
    main()
