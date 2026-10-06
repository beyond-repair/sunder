"""Packaging text must not outrun the claim ledger."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_description_is_claim_capped():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "autonomous coding agent" not in text.lower()
    assert "coding-agent sketch" in text
    assert "Not an autonomous coder." in text


def test_governance_and_security_docs_exist():
    gov = (ROOT / "GOVERNANCE.md").read_text(encoding="utf-8")
    sec = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "RESEARCH" in gov
    assert "Claim level:** ≤ 1" in gov
    assert "sovereign-clean-room" in gov
    assert "allowed_network" in sec
    assert "pynacl" in sec
