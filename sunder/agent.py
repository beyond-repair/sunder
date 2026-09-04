"""SUNDER Agent — the sovereign coding loop.

Honest v0.1: local tools only, no external LLM calls yet.
Architecture is ready for a real supervisor model.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

from sunder.aegis_bridge import session_graph
from sunder.fork import ForkManager
from sunder.gate import ConstitutionalGate, Risk
from sunder.vsa import VSAMemory

console = Console()

TEXT_SUFFIXES = {".py", ".md", ".txt", ".json", ".toml", ".yml", ".yaml", ".rs", ".ts", ".js", ".tsx", ".jsx"}

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
        self.gate = ConstitutionalGate(offline=offline, max_high_risk=8)
        self.forks = ForkManager(self.workspace)
        self.history: List[Dict[str, Any]] = []

    def tool_scan(self) -> Dict[str, Any]:
        def _scan():
            files = []
            for p in self.workspace.rglob("*"):
                if not p.is_file():
                    continue
                if any(part.startswith(".") for part in p.parts):
                    continue
                if p.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                try:
                    content = p.read_text(encoding="utf-8", errors="replace")
                    key = self.memory.remember_file(p, content)
                    files.append({"path": str(p.relative_to(self.workspace)), "key": key})
                except Exception:
                    pass
            return {"files_scanned": len(files), "memory": self.memory.stats(), "sample": files[:8]}

        result = self.gate.execute("scan", _scan, risk=Risk.LOW)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def tool_list_dir(self, rel: str = ".") -> Dict[str, Any]:
        def _list():
            target = (self.workspace / rel).resolve()
            if not target.is_relative_to(self.workspace):
                raise PermissionError("path escapes workspace")
            if not target.exists():
                raise FileNotFoundError(rel)
            entries = []
            for p in sorted(target.iterdir()):
                if p.name.startswith("."):
                    continue
                entries.append({"name": p.name, "type": "dir" if p.is_dir() else "file"})
            return {"path": rel, "entries": entries[:100]}

        result = self.gate.execute("list_dir", _list, risk=Risk.LOW)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def tool_search(self, pattern: str, max_hits: int = 20) -> Dict[str, Any]:
        def _search():
            rx = re.compile(pattern, re.IGNORECASE)
            hits = []
            for p in self.workspace.rglob("*"):
                if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                if any(part.startswith(".") for part in p.parts):
                    continue
                try:
                    for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                        if rx.search(line):
                            hits.append({
                                "path": str(p.relative_to(self.workspace)),
                                "line": i,
                                "text": line.strip()[:120],
                            })
                            if len(hits) >= max_hits:
                                return {"pattern": pattern, "hits": hits}
                except Exception:
                    pass
            return {"pattern": pattern, "hits": hits}

        result = self.gate.execute("search", _search, risk=Risk.LOW)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def tool_snap(self, description: str = "") -> Dict[str, Any]:
        def _snap():
            fork = self.forks.snap(description=description or f"auto-{int(time.time())}")
            return fork.summary()

        result = self.gate.execute("snap", _snap, risk=Risk.MEDIUM)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def tool_list_forks(self) -> Dict[str, Any]:
        result = self.gate.execute("list_forks", lambda: self.forks.list(), risk=Risk.LOW)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def tool_sunder(self, fork_id: str, keep: bool = True) -> Dict[str, Any]:
        result = self.gate.execute("sunder", lambda: self.forks.sunder(fork_id, keep=keep), risk=Risk.HIGH)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def tool_read(self, relpath: str) -> Dict[str, Any]:
        def _read():
            p = (self.workspace / relpath).resolve()
            if not p.is_relative_to(self.workspace):
                raise PermissionError("path escapes workspace")
            if not p.exists():
                raise FileNotFoundError(relpath)
            return p.read_text(encoding="utf-8", errors="replace")[:6000]

        result = self.gate.execute("read", _read, risk=Risk.LOW)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def tool_write(self, relpath: str, content: str) -> Dict[str, Any]:
        def _write():
            p = (self.workspace / relpath).resolve()
            if not p.is_relative_to(self.workspace):
                raise PermissionError("path escapes workspace")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            self.memory.remember_file(p, content)
            return {"written": relpath, "bytes": len(content)}

        result = self.gate.execute("write", _write, risk=Risk.HIGH)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def run(self, goal: str) -> Dict[str, Any]:
        console.print(f"\n[bold magenta]GOAL[/]  {goal}")
        console.print(f"[dim]workspace[/] {self.workspace}")
        console.print(f"[dim]mode[/]     {'OFFLINE' if self.offline else 'ONLINE'}\n")

        console.print("[cyan]-> SCAN[/] reading reality...")
        scan = self.tool_scan()
        self.history.append({"step": 0, "tool": "scan", **scan})
        if scan["gate"] == "PASS" and scan["data"]:
            console.print(f"   [green]ok[/] {scan['data']['files_scanned']} files -> VSA memory")

        console.print("[cyan]-> SNAP[/] creating version-fork...")
        snap = self.tool_snap(description=f"pre-goal: {goal[:60]}")
        self.history.append({"step": 1, "tool": "snap", **snap})
        fork_id = None
        if snap["gate"] == "PASS" and snap["data"]:
            fork_id = snap["data"]["id"]
            console.print(f"   [green]ok[/] fork {fork_id} ({snap['data']['files']} files)")

        listing = self.tool_list_dir(".")
        self.history.append({"step": 2, "tool": "list_dir", **listing})

        report = (
            f"# SUNDER Session Report\n\n"
            f"**Goal:** {goal}\n\n"
            f"**Workspace:** `{self.workspace}`\n\n"
            f"**Mode:** {'offline' if self.offline else 'online'}\n\n"
            f"**Fork:** `{fork_id}`\n"
        )
        write = self.tool_write(".sunder/session_report.md", report)
        self.history.append({"step": 3, "tool": "write", **write})

        graph = session_graph(goal, str(self.workspace), fork_id)
        manifest = json.dumps(graph.manifest(), indent=2)
        gwrite = self.tool_write(".sunder/aegis_manifest.json", manifest)
        self.history.append({"step": 3, "tool": "aegis_manifest", **gwrite})

        if fork_id:
            console.print(f"[cyan]-> SUNDER[/] keeping fork {fork_id}")
            sunder = self.tool_sunder(fork_id, keep=True)
            self.history.append({"step": 4, "tool": "sunder", **sunder})

        return {
            "status": "OK",
            "steps": len(self.history),
            "forks": len(self.forks.forks),
            "memory": self.memory.stats(),
            "gate": self.gate.summary(),
            "history": self.history,
        }
