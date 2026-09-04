"""Minimal AEGIS-compatible Artifact Graph for SUNDER sessions.

Conformance note: this is an interoperability adapter, not a new FLS primitive.
Identity is immutable; revisions are appended; relationships are typed.
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Artifact:
    identity: str
    kind: str
    revision: int
    properties: Dict[str, Any]
    locator: Optional[str] = None


@dataclass
class Relationship:
    kind: str
    source: str
    target: str


@dataclass
class ArtifactGraph:
    artifacts: Dict[str, Artifact] = field(default_factory=dict)
    relationships: List[Relationship] = field(default_factory=list)

    def add(self, artifact: Artifact) -> None:
        if artifact.identity in self.artifacts:
            existing = self.artifacts[artifact.identity]
            if existing.kind != artifact.kind:
                raise ValueError("identity kind collision")
            artifact.revision = existing.revision + 1
        self.artifacts[artifact.identity] = artifact

    def relate(self, kind: str, source: str, target: str) -> None:
        if source not in self.artifacts or target not in self.artifacts:
            raise ValueError("referential integrity failure")
        self.relationships.append(Relationship(kind=kind, source=source, target=target))

    def valid(self) -> bool:
        ids = set(self.artifacts)
        return all(r.source in ids and r.target in ids for r in self.relationships)

    def manifest(self) -> Dict[str, Any]:
        return {
            "fls_adapter": "sunder-aegis-bridge-0.1",
            "artifact_count": len(self.artifacts),
            "relationship_count": len(self.relationships),
            "valid": self.valid(),
            "artifacts": {
                i: {
                    "kind": a.kind,
                    "revision": a.revision,
                    "properties": a.properties,
                    "locator": a.locator,
                }
                for i, a in self.artifacts.items()
            },
            "relationships": [
                {"kind": r.kind, "source": r.source, "target": r.target}
                for r in self.relationships
            ],
        }


def session_graph(goal: str, workspace: str, fork_id: Optional[str]) -> ArtifactGraph:
    g = ArtifactGraph()
    sid = "session:" + hashlib.sha256(f"{goal}|{workspace}|{time.time()}".encode()).hexdigest()[:16]
    g.add(Artifact(sid, "SessionArtifact", 1, {"goal": goal, "workspace": workspace}))
    wid = "workspace:" + hashlib.sha256(workspace.encode()).hexdigest()[:16]
    g.add(Artifact(wid, "WorkspaceArtifact", 1, {"path": workspace}, locator=workspace))
    g.relate("OPERATES_ON", sid, wid)
    if fork_id:
        fid = f"fork:{fork_id}"
        g.add(Artifact(fid, "ForkArtifact", 1, {"fork_id": fork_id}))
        g.relate("SNAPPED", sid, fid)
    return g
