"""Version Forking — SNAP a parallel reality, experiment, then SUNDER.

Unlike git stash, this is an explicit agent-controlled reality branch.
"""
from __future__ import annotations

import shutil
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

@dataclass
class VersionFork:
    """A parallel snapshot of workspace state."""
    id: str
    root: Path
    created: float
    parent: Optional[str] = None
    description: str = ""
    files: Dict[str, str] = field(default_factory=dict)  # relpath -> content
    active: bool = True

    @classmethod
    def snap(cls, workspace: Path, description: str = "", parent: Optional[str] = None) -> "VersionFork":
        fid = str(uuid.uuid4())[:8]
        fork = cls(
            id=fid,
            root=workspace,
            created=time.time(),
            parent=parent,
            description=description or f"fork-{fid}",
        )
        # Capture text files only (honest scope for v0.1)
        for p in workspace.rglob("*"):
            if not p.is_file():
                continue
            if any(part.startswith(".") for part in p.parts):
                continue
            if p.suffix.lower() in {".py", ".md", ".txt", ".json", ".toml", ".yml", ".yaml", ".rs", ".ts", ".js"}:
                try:
                    rel = p.relative_to(workspace).as_posix()
                    fork.files[rel] = p.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    pass
        return fork

    def restore(self) -> int:
        """Write the forked state back to disk. Returns files written."""
        count = 0
        for rel, content in self.files.items():
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            count += 1
        return count

    def summary(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "files": len(self.files),
            "created": self.created,
            "parent": self.parent,
            "active": self.active,
        }

class ForkManager:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.forks: Dict[str, VersionFork] = {}
        self.current: Optional[str] = None

    def snap(self, description: str = "") -> VersionFork:
        parent = self.current
        fork = VersionFork.snap(self.workspace, description=description, parent=parent)
        self.forks[fork.id] = fork
        self.current = fork.id
        return fork

    def sunder(self, fork_id: str, keep: bool = True) -> Dict[str, Any]:
        """Commit (keep=True) or discard (keep=False) a fork."""
        fork = self.forks.get(fork_id)
        if not fork:
            return {"status": "FAIL", "error": "fork not found"}
        if keep:
            written = fork.restore()
            fork.active = False
            return {"status": "COMMITTED", "files_written": written, "id": fork_id}
        else:
            fork.active = False
            return {"status": "DISCARDED", "id": fork_id}

    def list(self) -> List[Dict[str, Any]]:
        return [f.summary() for f in self.forks.values()]
