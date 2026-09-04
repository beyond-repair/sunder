"""SUNDER Agent — the sovereign coding loop.

Honest v0.1: local tools only, no external LLM calls yet.
The architecture is ready for a real supervisor model.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table

from sunder.fork import ForkManager
from sunder.gate import ConstitutionalGate, Risk
from sunder.vsa import VSAMemory

console = Console()

class Agent:
    def __init__(
        self,
        workspace: Path,
        offline: bool = True,
        max_steps: int = 12,
        dim: int = 4096,
    ):
        self.workspace = workspace.resolve()
        self.offline = offline
        self.max_steps = max_steps
        self.memory = VSAMemory(dim=dim)
        self.gate = ConstitutionalGate(offline=offline)
        self.forks = ForkManager(self.workspace)
        self.history: List[Dict[str, Any]] = []

    # ── Tools (all go through the Gate) ──────────────────────────

    def tool_scan(self) -> Dict[str, Any]:
        """SCAN current reality."""
        def _scan():
            files = []
            for p in self.workspace.rglob("*"):
                if p.is_file() and not any(part.startswith(".") for part in p.parts):
                    if p.suffix.lower() in {".py", ".md", ".txt", ".json", ".toml"}:
                        try:
                            content = p.read_text(encoding="utf-8", errors="replace")
                            key = self.memory.remember_file(p, content)
                            files.append({"path": str(p.relative_to(self.workspace)), "key": key})
                        except Exception:
                            pass
            return {"files_scanned": len(files), "memory": self.memory.stats(), "sample": files[:8]}

        result = self.gate.execute("scan", _scan, risk=Risk.LOW)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def tool_snap(self, description: str = "") -> Dict[str, Any]:
        """SNAP a parallel version-fork."""
        def _snap():
            fork = self.forks.snap(description=description or f"auto-{int(time.time())}")
            return fork.summary()

        result = self.gate.execute("snap", _snap, risk=Risk.MEDIUM)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def tool_list_forks(self) -> Dict[str, Any]:
        def _list():
            return self.forks.list()

        result = self.gate.execute("list_forks", _list, risk=Risk.LOW)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def tool_sunder(self, fork_id: str, keep: bool = True) -> Dict[str, Any]:
        """SUNDER — commit or discard a fork."""
        def _sunder():
            return self.forks.sunder(fork_id, keep=keep)

        result = self.gate.execute("sunder", _sunder, risk=Risk.HIGH)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def tool_read(self, relpath: str) -> Dict[str, Any]:
        def _read():
            p = self.workspace / relpath
            if not p.exists():
                raise FileNotFoundError(relpath)
            return p.read_text(encoding="utf-8", errors="replace")[:4000]

        result = self.gate.execute("read", _read, risk=Risk.LOW)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def tool_write(self, relpath: str, content: str) -> Dict[str, Any]:
        def _write():
            p = self.workspace / relpath
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            self.memory.remember_file(p, content)
            return {"written": relpath, "bytes": len(content)}

        result = self.gate.execute("write", _write, risk=Risk.HIGH)
        return {"gate": result.status, "data": result.output, "error": result.error}

    # ── Main loop ────────────────────────────────────────────────

    def run(self, goal: str) -> Dict[str, Any]:
        console.print(f"\n[bold magenta]GOAL[/]  {goal}")
        console.print(f"[dim]workspace[/] {self.workspace}")
        console.print(f"[dim]mode[/]     {'OFFLINE' if self.offline else 'ONLINE'}\n")

        # Step 0 — always SCAN first
        console.print("[cyan]→ SCAN[/] reading reality…")
        scan = self.tool_scan()
        self.history.append({"step": 0, "tool": "scan", **scan})
        if scan["gate"] == "PASS":
            console.print(f"   [green]ok[/] {scan['data']['files_scanned']} files → VSA memory")

        # Step 1 — SNAP a safety fork before any mutation
        console.print("[cyan]→ SNAP[/] creating version-fork…")
        snap = self.tool_snap(description=f"pre-goal: {goal[:60]}")
        self.history.append({"step": 1, "tool": "snap", **snap})
        fork_id = None
        if snap["gate"] == "PASS" and snap["data"]:
            fork_id = snap["data"]["id"]
            console.print(f"   [green]ok[/] fork {fork_id} ({snap['data']['files']} files)")

        # Remaining steps — placeholder supervisor logic for v0.1
        # Real LLM planner will replace this in the next slice.
        console.print("[cyan]→ PLAN[/] (v0.1 heuristic supervisor)")
        console.print("   [dim]Real model-driven planning lands in the next vertical slice.[/]")
        console.print("   [dim]Architecture is ready: VSA + Gate + Forks are live.[/]")

        # Demo a safe write into a sunder report
        report = (
            f"# SUNDER Session Report\n\n"
            f"**Goal:** {goal}\n\n"
            f"**Workspace:** `{self.workspace}`\n\n"
            f"**Mode:** {'offline' if self.offline else 'online'}\n\n"
            f"**Fork:** `{fork_id}`\n\n"
            f"## Status\n\n"
            f"v0.1 runtime is live. SCAN and SNAP succeeded.\n"
            f"Constitutional Gate is enforcing fail-closed tool use.\n"
            f"VSA project memory has ingested the workspace.\n\n"
            f"Next: wire a real local/remote supervisor model.\n"
        )
        write = self.tool_write(".sunder/session_report.md", report)
        self.history.append({"step": 2, "tool": "write", **write})

        if write["gate"] == "PASS":
            console.print("   [green]ok[/] wrote .sunder/session_report.md")

        # Optional: keep the fork (it is already the current state)
        if fork_id:
            console.print(f"[cyan]→ SUNDER[/] keeping fork {fork_id} as working reality")
            sunder = self.tool_sunder(fork_id, keep=True)
            self.history.append({"step": 3, "tool": "sunder", **sunder})

        return {
            "status": "OK",
            "steps": len(self.history),
            "forks": len(self.forks.forks),
            "memory": self.memory.stats(),
            "gate": self.gate.summary(),
            "history": self.history,
        }
