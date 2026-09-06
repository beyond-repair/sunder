<div align="center">

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███████╗██╗   ██╗███╗   ██╗██████╗ ███████╗██████╗         ║
║   ██╔════╝██║   ██║████╗  ██║██╔══██║██╔════╝██╔══██║        ║
║   ███████╗██║   ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝        ║
║   ╚════██║██║   ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██║        ║
║   ███████║╚██████╔╝██║ ╚████║██████╔╝███████╗██║  ██║        ║
║   ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝        ║
║                                                              ║
║         ＳＣＡＮ  →  ＳＮＡＰ  →  ＳＵＮＤＥＲ                ║
╚══════════════════════════════════════════════════════════════╝
```

# SUNDER

### Local-first coding-agent experiment  
**Classification: RESEARCH / EXPERIMENTAL (Sweep-080)**

You are not the hero. You are the cold boot.

[![RESEARCH](https://img.shields.io/badge/●_RESEARCH-22d3ee?style=for-the-badge&labelColor=0f0f23)](https://github.com/beyond-repair/ADL-Governance)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-22d3ee?style=for-the-badge&labelColor=0f0f23)](#)
[![Offline](https://img.shields.io/badge/network__access-FALSE_by_default-ef4444?style=for-the-badge&labelColor=0f0f23)](#)
[![License](https://img.shields.io/badge/License-MIT-a855f7?style=for-the-badge&labelColor=0f0f23)](LICENSE)

```
CLAIM LEVEL  ≤ 1  (unit tests + local tools; no supervisor LLM)
PRODUCT      sovereign-clean-room is the ACTIVE offline runtime
```

</div>

---

## Claim policy (Sweep-080)

| Feature | State |
|---------|-------|
| Local tools + constitutional gate + VSA/fork tests | VERIFIED (CI run 33996778685 success, Sweep-078) |
| Supervisor LLM (local or remote) | PLANNED |
| Production autonomous coding agent | UNVERIFIED |
| Portfolio ACTIVE runtime | SUPERSEDED by `sovereign-clean-room` |

Do not treat this repository as the canonical agent product.

---

## Why SUNDER exists

Experiment toward: project memory that survives sessions, a fail-closed tool gate, and reversible version forks.

Honest v0.1 (code comment in `sunder/agent.py`): local tools only; no external LLM calls yet.

---

## The Loop

```text
  SCAN  →  SNAP  →  SUNDER
```

| # | Tool | Function | State |
|:-:|:----:|----------|-------|
| 1 | SCAN | Inspect project + VSA memory | PARTIAL |
| 2 | SNAP | Fork current reality | PARTIAL |
| 3 | SPIKE | High-risk action (gated) | PARTIAL |
| 4 | ANCHOR | Pin a stable checkpoint | PARTIAL |
| 5 | SUNDER | Commit or discard the fork | PARTIAL |

---

## Quick Start

```bash
git clone https://github.com/beyond-repair/sunder.git
cd sunder
pip install -r requirements.txt
python -m sunder "Refactor the authentication module and add tests"
```

Expect heuristic / local-tool behavior, not a live supervisor LLM.

---

[Atomic Dream Labs](https://github.com/beyond-repair) · governed by [ADL-Governance](https://github.com/beyond-repair/ADL-Governance)
