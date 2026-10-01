# Claim Status — sunder

**Sweep:** 181  
**Classification:** RESEARCH  
**Claim level:** ≤ 1  
**Head basis:** pre-lock `7ca2d2aa9fb50db0702ee07028bb2429316269ff`  
**Canonical product runtime:** `sovereign-clean-room` (ACTIVE). This repo is not that runtime.

## Allowed

| Statement | Evidence |
|-----------|----------|
| Local tools, constitutional gate, VSA bind/unbind, and version-fork snap exist | `sunder/agent.py`, `gate.py`, `vsa.py`, `fork.py` |
| Offline default refuses network-requiring calls | `tests/test_core.py::test_gate_refuses_network_when_offline` |
| High-risk budget refuses the call past `max_high_risk` | `tests/test_core.py::test_gate_high_risk_budget` |
| Path escape fails closed | `tests/test_core.py::test_agent_smoke_and_tools` |

## Not claimed

| Statement | State |
|-----------|--------|
| Supervisor LLM (local or remote) | PLANNED |
| Production autonomous coding agent | UNVERIFIED |
| Portfolio ACTIVE runtime | not this repo; see `sovereign-clean-room` |
| Measured benchmark scores | not evidenced; `docs/BENCHMARK_CORPUS.md` is a protocol, not a result |
| Release tag | none at Sweep-181 select |

Do not promote this repository without a green CI run on the lock commit and an operator claim review.
