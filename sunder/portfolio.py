"""Deterministic portfolio catalog for beyond-repair / Atomic Dream Labs.

A1: Catalog derived from GitHub search user:beyond-repair on 2026-09-04 (65 public repos).
This module does not scrape live GitHub; it is a locked inventory for compatibility planning.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class RepoRecord:
    name: str
    cluster: str
    status: str  # LIVE | STUB | ARCHIVE | DUPLICATE | EMPTY
    functions: tuple[str, ...]
    missing: tuple[str, ...]
    compatible_with: tuple[str, ...]


REPOS: tuple[RepoRecord, ...] = (
    RepoRecord("sunder", "agent-runtime", "LIVE", ("SCAN", "SNAP", "SUNDER", "constitutional_gate", "fhrr_vsa", "workspace_tools"), ("supervisor_llm", "aegis_artifact_export", "clean_room_vsa_interop"), ("sovereign-clean-room", "forge-aegis", "ADL-SEEM", "Sovereign-OS")),
    RepoRecord("ADL-Governance", "governance", "LIVE", ("portfolio_constitution", "lifecycle", "claim_validation"), ("automated_claim_linter_across_all_repos",), ("ADL-SEEM", "sunder", "forge-aegis")),
    RepoRecord("ADL-SEEM", "governance", "LIVE", ("response_contract", "evidence_hierarchy", "session_state_object"), ("machine-checkable schema enforcement",), ("sunder", "SEEM-2.0-Self-Evolving-Emergent-Mind")),
    RepoRecord("forge-aegis", "integrity", "LIVE", ("fls_ontology", "artifact_identity_revision", "relationship_graph"), ("runtime_measurement_daemon", "signed_baseline_store"), ("AEGIS-Project-Nehemiah-", "sunder")),
    RepoRecord("sovereign-clean-room", "memory", "LIVE", ("fhrr_engine", "banel", "invertibility_gate"), ("sunder_adapter_package",), ("sunder", "seem-block-system")),
    RepoRecord("Sovereign-OS", "os-constitution", "LIVE", ("human_uptime", "default_refusal"), ("executable_policy_kernel",), ("SovereignOS", "sunder")),
    RepoRecord("coherence-drive", "physics-cft", "LIVE", ("vacuum_coherent_engine_integration",), ("independent_experimental_replication",), ("stress-tensor-modification", "momentum-closure")),
    RepoRecord("Digital_Double_virtual_workforce", "workforce", "LIVE", ("virtual_agents", "task_automation"), ("sunder_tool_backend", "dedup_lineage"), ("sunder",)),
    RepoRecord("SEEM-2.0-Self-Evolving-Emergent-Mind", "seem", "LIVE", ("offline_symbolic_substrate",), ("sunder_supervisor_hook",), ("sunder",)),
    RepoRecord("Project-Cold-Boot", "games", "LIVE", ("godot_reality_editing",), ("sunder_mod_pipeline",), ("blacksite", "RealityOS")),
)


def by_cluster() -> Dict[str, List[RepoRecord]]:
    out: Dict[str, List[RepoRecord]] = {}
    for r in REPOS:
        out.setdefault(r.cluster, []).append(r)
    return out


def gaps() -> List[RepoRecord]:
    return [r for r in REPOS if r.missing]


def build_priorities() -> List[str]:
    return [
        "sunder: supervisor LLM slice (local, gated)",
        "sunder: AEGIS artifact export for SCAN/SNAP/SUNDER events",
        "sunder: adapter to sovereign-clean-room FHRR if package is installable",
        "ADL-Governance: automated duplicate/empty repo retirement list",
        "workforce line: single canonical Digital Double + sunder tool backend",
        "SEEM line: collapse three microservice repos; hook as SUNDER supervisor",
        "physics-cft: shared numeric verification package (do not mix with agent runtime)",
    ]
