# Claim Status — sunder

**Classification:** RESEARCH  
**Claim level:** ≤ 1  
**Version:** 0.1.1 heuristic  
**Canonical product runtime:** this repository is not `sovereign-clean-room` and does not import it. That other repo is an offline VSA sketch, not a mind.

## Allowed

| Statement | Evidence |
|-----------|----------|
| Local tools, constitutional gate, VSA bind/unbind, and version-fork snap exist | `sunder/agent.py`, `gate.py`, `vsa.py`, `fork.py` |
| Offline default refuses network-requiring calls, and `--online` still refuses them because `allowed_network` stays false | `tests/test_core.py::test_gate_refuses_network_when_offline`, `tests/test_repair.py::test_online_flag_still_refuses_network` |
| High-risk budget refuses the call past `max_high_risk` | `tests/test_core.py::test_gate_high_risk_budget` |
| Path escape fails closed, including a sibling directory whose name shares a prefix | `tests/test_repair.py::test_prefix_sibling_does_not_escape` |
| T-001 writes `is_palindrome` and a test that pytest can run, on a scratch workspace | `python -m sunder --demo T-001` |
| T-003 refuses the fetch and does not edit README | `python -m sunder --demo T-003` |
| T-004 injects a syntax error and `sunder(keep=True)` restores the snap | `python -m sunder --demo T-004` |

## Not claimed

| Statement | State |
|-----------|--------|
| Supervisor LLM (local or remote) | not in this tree |
| Production autonomous coding agent | not this program |
| T-002 behavior-preserving rename of `gate.py` | not implemented; CLI exit 3 |
| Measured benchmark success rate | not published; one scripted demo is not a score |
| `keep=True` is a git commit of later edits | false; it writes the snapshot back |
| Release tag | none |

`sunder(keep=True)` re-anchors files that were in the snap. `keep=False` leaves the workspace unchanged and retires the fork record.
