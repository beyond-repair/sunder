"""SUNDER Agent — the sovereign coding loop.

Honest v0.1: local tools only, no external LLM calls yet.
Benchmark ids T-001, T-003, and T-004 are deterministic heuristics.
T-002 is recognized and refused as unimplemented. There is no supervisor model.
"""
from __future__ import annotations

import ast
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

from sunder.fork import ForkManager
from sunder.gate import ConstitutionalGate, Risk
from sunder.tasks import (
    PALINDROME_SOURCE,
    PALINDROME_TEST,
    SYNTAX_BROKEN,
    SYNTAX_SEED,
    resolve_task,
)
from sunder.vsa import VSAMemory

console = Console()


def _hidden_relative(root: Path, path: Path) -> bool:
    """True when a path sits in a dot-directory *inside* root.

    Absolute parents such as ``.../.sunder/demo`` are the workspace itself
    and must not hide the project. ``.git`` / ``.venv`` under root still skip.
    """
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        return True
    return any(part.startswith(".") for part in rel.parts)


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
        self.gate = ConstitutionalGate(offline=offline)
        self.forks = ForkManager(self.workspace)
        self.history: List[Dict[str, Any]] = []

    def _contained(self, rel: str) -> Path:
        """Resolve rel inside the workspace or raise PermissionError.

        A prefix check is not enough: workspace ``/tmp/proj`` must not accept
        ``/tmp/proj-evil``. ``Path.is_relative_to`` after resolve is the jail.
        """
        root = self.workspace.resolve()
        candidate = Path(rel)
        target = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
        if not target.is_relative_to(root):
            raise PermissionError("path escapes workspace")
        try:
            parts = target.relative_to(root).parts
        except ValueError as exc:
            raise PermissionError("path escapes workspace") from exc
        if ".git" in parts:
            raise PermissionError("refusing .git path")
        return target

    def _is_source_tree(self) -> bool:
        """True when workspace is this repository, not a scratch demo dir."""
        return (self.workspace / "sunder" / "agent.py").is_file() and (
            self.workspace / "CLAIM_STATUS.md"
        ).is_file()

    def _record(self, tool: str, result: Dict[str, Any]) -> None:
        self.history.append({"step": len(self.history), "tool": tool, **result})

    def _capped(self) -> bool:
        return len(self.history) >= self.max_steps

    # ── Tools (all go through the Gate) ──────────────────────────

    def tool_scan(self) -> Dict[str, Any]:
        """SCAN current reality into VSA memory."""
        def _scan():
            files = []
            for p in self.workspace.rglob("*"):
                if not p.is_file():
                    continue
                if _hidden_relative(self.workspace, p):
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
            target = self._contained(rel)
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
            import re
            rx = re.compile(pattern, re.IGNORECASE)
            hits = []
            for p in self.workspace.rglob("*"):
                if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                if _hidden_relative(self.workspace, p):
                    continue
                try:
                    resolved = p.resolve()
                    if not resolved.is_relative_to(self.workspace):
                        continue
                    for i, line in enumerate(resolved.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
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
            p = self._contained(relpath)
            if not p.exists() or not p.is_file():
                raise FileNotFoundError(relpath)
            return p.read_text(encoding="utf-8", errors="replace")[:6000]

        result = self.gate.execute("read", _read, risk=Risk.LOW)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def tool_write(self, relpath: str, content: str) -> Dict[str, Any]:
        def _write():
            p = self._contained(relpath)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            self.memory.remember_file(p, content)
            return {"written": relpath, "bytes": len(content)}

        result = self.gate.execute("write", _write, risk=Risk.HIGH)
        return {"gate": result.status, "data": result.output, "error": result.error}

    def tool_network(self, name: str = "fetch") -> Dict[str, Any]:
        """Ask the gate for a network call. v0.1 never performs the call."""
        result = self.gate.execute(
            name,
            lambda: (_ for _ in ()).throw(RuntimeError("network body is not implemented")),
            risk=Risk.HIGH,
            requires_network=True,
        )
        return {"gate": result.status, "data": result.output, "error": result.error}

    # ── Main loop ────────────────────────────────────────────────

    def run(self, goal: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            resolved_id, kind = resolve_task(goal, task_id)
        except KeyError:
            return {
                "status": "FAIL",
                "steps": 0,
                "forks": 0,
                "error": f"unknown task id: {task_id}",
                "history": [],
            }

        console.print(f"\n[bold magenta]GOAL[/]  {goal}")
        console.print(f"[dim]workspace[/] {self.workspace}")
        console.print(f"[dim]mode[/]     {'OFFLINE' if self.offline else 'ONLINE'}")
        console.print(f"[dim]heuristic[/] {kind}" + (f" ({resolved_id})" if resolved_id else ""))
        console.print("[dim]supervisor model[/] none — local tools only\n")

        blocked_source_tree = kind in {"palindrome", "restore_syntax"} and self._is_source_tree()
        task_met: Optional[bool] = None
        note = ""

        if not self._capped():
            console.print("[cyan]→ SCAN[/] reading reality…")
            scan = self.tool_scan()
            self._record("scan", scan)
            if scan["gate"] == "PASS" and scan["data"]:
                console.print(f"   [green]ok[/] {scan['data']['files_scanned']} files → VSA memory")

        fork_id = None
        if not self._capped():
            console.print("[cyan]→ SNAP[/] creating version-fork…")
            snap = self.tool_snap(description=f"pre-goal: {goal[:60]}")
            self._record("snap", snap)
            if snap["gate"] == "PASS" and snap["data"]:
                fork_id = snap["data"]["id"]
                console.print(f"   [green]ok[/] fork {fork_id} ({snap['data']['files']} files)")

        if blocked_source_tree:
            note = (
                "refusing to edit the sunder source tree; "
                "re-run with --demo so the heuristic uses .sunder/demo/<task>/"
            )
            task_met = False
            console.print(f"[yellow]→ HOLD[/] {note}")
            kind = "report"
        elif kind == "network":
            task_met, note = self._do_network()
        elif kind == "palindrome":
            task_met, note = self._do_palindrome(fork_id)
        elif kind == "restore_syntax":
            task_met, note, fork_id = self._do_restore_syntax(fork_id)
        elif kind == "unimplemented":
            task_met = False
            note = "T-002 rename is not implemented by the v0.1 heuristic; gate.py was not edited"
            console.print(f"[yellow]→ HOLD[/] {note}")

        if kind == "report" or kind == "unimplemented":
            self._write_session_report(goal, fork_id, note)

        if fork_id and not self._capped() and kind != "restore_syntax":
            # keep=True writes the snap back. New files the heuristic added
            # after SNAP (T-001) are not in the snap, so they remain.
            console.print(f"[cyan]→ SUNDER[/] re-anchor workspace to snap {fork_id} (keep=True)")
            sunder = self.tool_sunder(fork_id, keep=True)
            self._record("sunder", sunder)

        status = "OK"
        if task_met is False and kind == "palindrome":
            status = "FAIL"
        if any(step.get("gate") == "FAIL" and step.get("tool") in {"write", "snap", "sunder"} for step in self.history):
            if kind == "palindrome":
                status = "FAIL"

        return {
            "status": status,
            "steps": len(self.history),
            "forks": len(self.forks.forks),
            "memory": self.memory.stats(),
            "gate": self.gate.summary(),
            "history": self.history,
            "task_id": resolved_id,
            "task_kind": kind if not blocked_source_tree else "blocked_source_tree",
            "task_met": task_met,
            "blocked_source_tree": blocked_source_tree,
            "note": note,
            "fork_id": fork_id,
        }

    def _do_network(self) -> tuple[bool, str]:
        if self._capped():
            return False, "stopped at max_steps before the network gate"
        console.print("[cyan]→ GATE[/] network tool requested; body will not run")
        refused = self.tool_network("fetch_peps")
        self._record("fetch_peps", refused)
        readme = self.workspace / "README.md"
        before = readme.read_text(encoding="utf-8") if readme.is_file() else None
        ok = refused["gate"] == "REFUSED" and "network" in (refused["error"] or "")
        if readme.is_file():
            after = readme.read_text(encoding="utf-8")
            ok = ok and after == before
        note = "network refused; no fetch performed; README unchanged" if ok else "network gate did not refuse"
        style = "green" if ok else "red"
        console.print(f"   [{style}]{refused['gate']}[/] {refused['error']}")
        return ok, note

    def _do_palindrome(self, fork_id: Optional[str]) -> tuple[bool, str]:
        del fork_id
        if self._capped():
            return False, "stopped at max_steps before writes"
        console.print("[cyan]→ WRITE[/] heuristic is_palindrome (not a model)")

        def _write_all():
            # One high-risk gate call: both corpus paths, plus a package marker
            # so `sunder.utils` imports from the scratch workspace.
            self._contained("sunder/utils.py")
            self._contained("sunder/__init__.py")
            self._contained("tests/test_utils.py")
            pkg = self.workspace / "sunder"
            pkg.mkdir(parents=True, exist_ok=True)
            init = pkg / "__init__.py"
            if not init.exists():
                init.write_text('"""Scratch package created by the T-001 heuristic.\n"""\n', encoding="utf-8")
            (pkg / "utils.py").write_text(PALINDROME_SOURCE, encoding="utf-8")
            tests = self.workspace / "tests"
            tests.mkdir(parents=True, exist_ok=True)
            (tests / "test_utils.py").write_text(PALINDROME_TEST, encoding="utf-8")
            self.memory.remember_file(pkg / "utils.py", PALINDROME_SOURCE)
            return {"written": ["sunder/utils.py", "tests/test_utils.py"], "bytes": len(PALINDROME_SOURCE) + len(PALINDROME_TEST)}

        written = self.gate.execute("write", _write_all, risk=Risk.HIGH)
        result = {"gate": written.status, "data": written.output, "error": written.error}
        self._record("write", result)
        ok = written.status == "PASS"
        note = "wrote sunder/utils.py and tests/test_utils.py" if ok else "palindrome writes were refused or failed"
        return ok, note

    def _do_restore_syntax(self, fork_id: Optional[str]) -> tuple[bool, str, Optional[str]]:
        rel = "sunder/agent.py"
        target = self.workspace / rel
        if not target.is_file() and not self._capped():
            console.print("[cyan]→ SEED[/] sunder/agent.py was missing; writing a valid stub before SNAP")
            seeded = self.tool_write(rel, SYNTAX_SEED)
            self._record("write", seeded)
            if seeded["gate"] != "PASS":
                return False, "could not seed sunder/agent.py", fork_id
            # The first SNAP ran before this seed. Take another so restore has the valid text.
            if not self._capped():
                console.print("[cyan]→ SNAP[/] re-snap after seed")
                snap = self.tool_snap(description="post-seed valid agent.py")
                self._record("snap", snap)
                if snap["gate"] == "PASS" and snap["data"]:
                    fork_id = snap["data"]["id"]
        if fork_id is None:
            return False, "no snap to restore", fork_id
        if self._capped():
            return False, "stopped at max_steps before the syntax injection", fork_id
        console.print("[cyan]→ WRITE[/] deliberate syntax error inside the snap")
        broken = self.tool_write(rel, SYNTAX_BROKEN)
        self._record("write", broken)
        if broken["gate"] != "PASS":
            return False, "syntax injection was not written", fork_id
        if self._capped():
            return False, "stopped at max_steps before restore", fork_id
        console.print(f"[cyan]→ SUNDER[/] restore snap {fork_id} (keep=True writes the snapped bytes back)")
        restored = self.tool_sunder(fork_id, keep=True)
        self._record("sunder", restored)
        final = target.read_text(encoding="utf-8") if target.is_file() else ""
        clean = "BROKEN_SYNTAX" not in final
        try:
            ast.parse(final)
            parses = True
        except SyntaxError:
            parses = False
        committed = bool(restored["data"] and restored["data"].get("status") == "COMMITTED")
        ok = restored["gate"] == "PASS" and committed and clean and parses
        note = (
            "injected BROKEN_SYNTAX then sunder(keep=True) restored the snap; "
            "keep=False would have left the broken file on disk"
            if ok
            else "restore did not return the file to a parseable pre-injection state"
        )
        return ok, note, fork_id

    def _write_session_report(self, goal: str, fork_id: Optional[str], note: str) -> None:
        if self._capped():
            console.print("[yellow]→ WRITE[/] skipped session report (max_steps)")
            return
        report = (
            f"# SUNDER Session Report\n\n"
            f"**Goal:** {goal}\n\n"
            f"**Workspace:** `{self.workspace}`\n\n"
            f"**Mode:** {'offline' if self.offline else 'online'}\n\n"
            f"**Fork:** `{fork_id}`\n\n"
            f"## Status\n\n"
            f"v0.1 runtime is a local-tool heuristic. There is no supervisor LLM.\n"
            f"- SCAN ingested the workspace into VSA memory.\n"
            f"- SNAP stored a reversible text snapshot.\n"
            f"- Constitutional Gate enforced fail-closed tool use.\n"
            f"- list_dir / search / read / write tools are available.\n\n"
            f"{note}\n\n"
            f"Network tools stay refused while allowed_network is false, "
            f"including when the CLI is passed --online.\n"
        )
        write = self.tool_write(".sunder/session_report.md", report)
        self._record("write", write)
        if write["gate"] == "PASS":
            console.print("   [green]ok[/] wrote .sunder/session_report.md")
