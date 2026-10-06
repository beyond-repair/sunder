<div align="center">

```
╔═════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███████╗██╗   ██╗███╗   ██╗██████╗ ███████╗██████╗         ║
║   ██╔════╝██║   ██║████╗  ██║██╔══██║██╔════╝██╔══██║        ║
║   ███████╗██║   ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝        ║
║   ╚════██║██║   ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██║        ║
║   ███████║╚██████╔╝██║ ╚████║██████╔╝███████╗██║  ██║        ║
║   ╚══════╝ ╚═════╝  ╚═╝  ╚═══╝╚═════╝  ╚══════╝╚═╝  ╚═╝        ║
║                                                              ║
║         ＳＣＡＮ  →  ＳＮＡＰ  →  ＳＵＮＤＥＲ                ║
╚═════════════════════════════════════════════════════════════╝
```

# SUNDER

### Local-first coding-agent experiment  
**Classification: RESEARCH / EXPERIMENTAL (Sweep-181 reconfirm; first lock Sweep-080)**

You are not the hero. You are the cold boot.

[![RESEARCH](https://img.shields.io/badge/●_RESEARCH-22d3ee?style=for-the-badge&labelColor=0f0f23)](https://github.com/beyond-repair/ADL-Governance)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-22d3ee?style=for-the-badge&labelColor=0f0f23)](#)
[![Offline](https://img.shields.io/badge/network__access-FALSE_by_default-ef4444?style=for-the-badge&labelColor=0f0f23)](#)
[![License](https://img.shields.io/badge/License-MIT-a855f7?style=for-the-badge&labelColor=0f0f23)](LICENSE)

```
CLAIM LEVEL  ≤ 1  (unit tests + local heuristic; no supervisor LLM)
PRODUCT      runnable sketch — not an autonomous coder, not a mind
```

</div>

---

## Claim policy (v0.1.1)

| Feature | State |
|---------|-------|
| Install, SCAN / SNAP / SUNDER, VSA bind-unbind, constitutional gate | RUNNABLE in v0.1. Heuristic only |
| Corpus demos T-001, T-003, T-004 | Deterministic local heuristic. Not a model |
| T-002 (rename `gate.py`) | NOT IMPLEMENTED. CLI exits 3 and does not edit the file |
| Supervisor LLM (local or remote) | NOT IN THIS TREE |
| Production autonomous coding agent | NOT THIS PROGRAM |
| Portfolio ACTIVE runtime | NOT this repo. `sovereign-clean-room` is a separate offline VSA sketch, not a mind, and it is not imported here |

Do not treat this repository as an autonomous coder or as the canonical agent product.

Claim ledger: [CLAIM_STATUS.md](CLAIM_STATUS.md). Governance: [GOVERNANCE.md](GOVERNANCE.md). Security notes: [SECURITY.md](SECURITY.md).

---

## What actually runs

`python -m sunder` is a fixed local loop:

1. **SCAN** — read text files under the workspace into an in-memory FHRR vector (NumPy).
2. **SNAP** — copy those texts into a `VersionFork`.
3. **Heuristic** — only the four corpus prompts in `docs/benchmark_tasks/` select an action. Any other goal writes `.sunder/session_report.md` and stops.
4. **SUNDER `keep=True`** — write the snapped bytes back. That undoes edits to files that were already in the snap. Files created after the snap stay. `keep=False` retires the fork and leaves the disk alone.

`--online` clears the offline flag only. `allowed_network` stays false, so a network tool is still refused. v0.1 does not call the network.

`pynacl` and `httpx` are installed from `requirements.txt` and are not used by this loop.

---

## Install, run, test

Requires Python 3.11+ (`python3` on the path; a `python` alias is not required). From a clean clone:

```bash
git clone https://github.com/beyond-repair/sunder.git
cd sunder
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
python -m pytest -q
python -m sunder "Inspect this project"
python -m sunder --demo T-001
python -m sunder --demo T-003
python -m sunder --demo T-004
```

`--demo` writes under `<workspace>/.sunder/demo/<id>/` (gitignored). It does not modify `sunder/agent.py` in the clone. T-001's pytest is part of that command (3 checks). T-002 exits 3.

| Exit | Meaning |
|-----:|---------|
| 0 | Loop finished. Generic goal, or T-001 / T-003 / T-004 met |
| 1 | Tool failure or T-001 pytest failed |
| 3 | Task not met (T-002, or a corpus task that did not meet its check) |
| 4 | Refused to apply T-001 or T-004 to a checkout that contains `sunder/agent.py` and `CLAIM_STATUS.md` |

Configuration flags: `--workspace`, `--max-steps` (stops the loop after N tool records), `--offline` / `--online` (see above). There is no config file and no API key.

Passing an exact corpus prompt as the goal, against a scratch directory, runs the same heuristic. Against this clone it exits 4 instead of editing the library.

---

## The Loop

```text
  SCAN  →  SNAP  →  SUNDER
```

| # | Tool | Function | State |
|:-:|:----:|----------|-------|
| 1 | SCAN | Text files → in-memory VSA | v0.1 |
| 2 | SNAP | In-memory text snapshot | v0.1 |
| 3 | SPIKE | High-risk tool, gated | v0.1 budget (`max_high_risk=3`) |
| 4 | ANCHOR | `sunder(keep=True)` restores the snap | v0.1 |
| 5 | SUNDER | Restore (`keep=True`) or retire (`keep=False`) | v0.1 |

---

[Atomic Dream Labs](https://github.com/beyond-repair) · governed by [ADL-Governance](https://github.com/beyond-repair/ADL-Governance)
