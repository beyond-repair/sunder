"""Core tests for SUNDER v0.1 — must stay green."""
from __future__ import annotations

import tempfile
from pathlib import Path

from sunder.vsa import VSAMemory
from sunder.gate import ConstitutionalGate, Risk
from sunder.fork import ForkManager
from sunder.agent import Agent

def test_vsa_bind_unbind():
    m = VSAMemory(dim=512, seed=42)
    a = m.register("A")
    b = m.register("B")
    c = m.bind(a, b)
    recovered = m.unbind(c, b)
    assert m.similarity(recovered, a) > 0.9

def test_gate_refuses_network_when_offline():
    g = ConstitutionalGate(offline=True, allowed_network=False)
    r = g.execute("net", lambda: "no", risk=Risk.LOW, requires_network=True)
    assert r.status == "REFUSED"

def test_gate_allows_low_risk():
    g = ConstitutionalGate(offline=True)
    r = g.execute("ok", lambda: 42, risk=Risk.LOW)
    assert r.status == "PASS"
    assert r.output == 42

def test_version_fork_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "hello.py").write_text("print('hi')\n", encoding="utf-8")
        fm = ForkManager(root)
        fork = fm.snap("test")
        assert "hello.py" in fork.files
        (root / "hello.py").write_text("print('changed')\n", encoding="utf-8")
        result = fm.sunder(fork.id, keep=True)
        assert result["status"] == "COMMITTED"
        assert (root / "hello.py").read_text(encoding="utf-8") == "print('hi')\n"

def test_agent_smoke_and_tools():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "main.py").write_text("x = 1\n# marker_alpha\n", encoding="utf-8")
        (root / "docs").mkdir()
        (root / "docs" / "note.md").write_text("# hello\n", encoding="utf-8")

        agent = Agent(workspace=root, offline=True, max_steps=6)

        # unit-level tool checks
        listing = agent.tool_list_dir(".")
        assert listing["gate"] == "PASS"
        names = {e["name"] for e in listing["data"]["entries"]}
        assert "main.py" in names
        assert "docs" in names

        search = agent.tool_search("marker_alpha")
        assert search["gate"] == "PASS"
        assert any("marker_alpha" in h["text"] for h in search["data"]["hits"])

        # path escape must fail closed
        bad = agent.tool_read("../outside.txt")
        assert bad["gate"] in ("FAIL", "REFUSED")

        # full run
        result = agent.run("Inspect the project")
        assert result["status"] == "OK"
        assert result["steps"] >= 3
        assert (root / ".sunder" / "session_report.md").exists()
