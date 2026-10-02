"""Repair checks: path jail, public imports, and the bounded corpus heuristic."""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from sunder import Agent, ConstitutionalGate, ForkManager, VersionFork, VSAMemory
from sunder.__main__ import main
from sunder.gate import Risk
from sunder.tasks import T001_PROMPT, T003_PROMPT, T004_PROMPT


def test_public_imports():
    assert Agent and VSAMemory and ConstitutionalGate and VersionFork and ForkManager


def test_prefix_sibling_does_not_escape(tmp_path: Path):
    root = tmp_path / "proj"
    evil = tmp_path / "proj-evil"
    root.mkdir()
    evil.mkdir()
    (evil / "secret.txt").write_text("nope", encoding="utf-8")
    agent = Agent(workspace=root, offline=True)
    bad = agent.tool_read("../proj-evil/secret.txt")
    assert bad["gate"] == "FAIL"
    assert bad["data"] is None
    assert "nope" not in str(bad["error"])
    write = agent.tool_write("../proj-evil/planted.txt", "x")
    assert write["gate"] == "FAIL"
    assert not (evil / "planted.txt").exists()
    git_write = agent.tool_write(".git/config", "x")
    assert git_write["gate"] == "FAIL"
    assert not (root / ".git" / "config").exists()


def test_online_flag_still_refuses_network():
    gate = ConstitutionalGate(offline=False, allowed_network=False)
    result = gate.execute("fetch", lambda: "should-not-run", risk=Risk.HIGH, requires_network=True)
    assert result.status == "REFUSED"
    assert result.output is None


def test_t001_heuristic_writes_palindrome(tmp_path: Path):
    agent = Agent(workspace=tmp_path, offline=True)
    result = agent.run(T001_PROMPT)
    assert result["status"] == "OK"
    assert result["task_id"] == "T-001"
    assert result["task_met"] is True
    utils = (tmp_path / "sunder" / "utils.py").read_text(encoding="utf-8")
    ast.parse(utils)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests/test_utils.py", "--tb=short"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_t003_refuses_network_and_leaves_readme(tmp_path: Path):
    readme = tmp_path / "README.md"
    readme.write_text("LOCAL ONLY\n", encoding="utf-8")
    agent = Agent(workspace=tmp_path, offline=True)
    result = agent.run(T003_PROMPT)
    assert result["task_met"] is True
    assert result["status"] == "OK"
    assert readme.read_text(encoding="utf-8") == "LOCAL ONLY\n"
    assert any(step["tool"] == "fetch_peps" and step["gate"] == "REFUSED" for step in result["history"])


def test_t004_restore_clears_syntax_error(tmp_path: Path):
    target = tmp_path / "sunder" / "agent.py"
    target.parent.mkdir(parents=True)
    target.write_text("def ok():\n    return 1\n", encoding="utf-8")
    agent = Agent(workspace=tmp_path, offline=True)
    result = agent.run(T004_PROMPT)
    assert result["task_met"] is True, result
    final = target.read_text(encoding="utf-8")
    assert "BROKEN_SYNTAX" not in final
    ast.parse(final)
    assert any(step["tool"] == "sunder" and step["data"]["status"] == "COMMITTED" for step in result["history"])


def test_source_tree_is_not_rewritten(tmp_path: Path):
    (tmp_path / "sunder").mkdir()
    (tmp_path / "sunder" / "agent.py").write_text("def ok():\n    return 1\n", encoding="utf-8")
    (tmp_path / "CLAIM_STATUS.md").write_text("locked\n", encoding="utf-8")
    original = (tmp_path / "sunder" / "agent.py").read_text(encoding="utf-8")
    agent = Agent(workspace=tmp_path, offline=True)
    result = agent.run(T004_PROMPT)
    assert result["blocked_source_tree"] is True
    assert result["task_met"] is False
    assert (tmp_path / "sunder" / "agent.py").read_text(encoding="utf-8") == original
    assert not (tmp_path / "sunder" / "utils.py").exists()


def test_generic_goal_does_not_invent_files(tmp_path: Path):
    agent = Agent(workspace=tmp_path, offline=True, max_steps=6)
    result = agent.run("Inspect the project")
    assert result["status"] == "OK"
    assert result["task_met"] is None
    assert result["steps"] >= 3
    assert (tmp_path / ".sunder" / "session_report.md").exists()
    assert not (tmp_path / "sunder" / "utils.py").exists()


def test_max_steps_stops_early(tmp_path: Path):
    agent = Agent(workspace=tmp_path, offline=True, max_steps=1)
    result = agent.run("Inspect the project")
    assert result["steps"] == 1
    assert result["history"][0]["tool"] == "scan"
    assert not (tmp_path / ".sunder" / "session_report.md").exists()


def test_cli_demo_t001_and_t002(tmp_path: Path):
    runner = CliRunner()
    ok = runner.invoke(main, ["--demo", "T-001", "--workspace", str(tmp_path)])
    assert ok.exit_code == 0, ok.output
    assert (tmp_path / ".sunder" / "demo" / "T-001" / "sunder" / "utils.py").is_file()
    hold = runner.invoke(main, ["--demo", "T-002", "--workspace", str(tmp_path)])
    assert hold.exit_code == 3, hold.output
    assert "not implemented" in hold.output.lower() or "met=False" in hold.output


def test_hidden_parent_workspace_still_snaps(tmp_path: Path):
    root = tmp_path / ".hidden" / "proj"
    root.mkdir(parents=True)
    (root / "hello.py").write_text("print(1)\n", encoding="utf-8")
    (root / ".secret").mkdir()
    (root / ".secret" / "no.py").write_text("x\n", encoding="utf-8")
    fork = ForkManager(root).snap("hidden-parent")
    assert "hello.py" in fork.files
    assert ".secret/no.py" not in fork.files
    agent = Agent(workspace=root, offline=True)
    scan = agent.tool_scan()
    assert scan["gate"] == "PASS"
    assert scan["data"]["files_scanned"] == 1


def test_prompt_files_match_task_table():
    from sunder.tasks import TASKS
    root = Path(__file__).resolve().parents[1] / "docs" / "benchmark_tasks"
    for task_id, spec in TASKS.items():
        text = (root / f"{task_id}.prompt.txt").read_text(encoding="utf-8").strip()
        assert text == spec["prompt"]
