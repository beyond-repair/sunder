# Security — sunder

Research sketch. No production security claim.

- Default mode is offline. `--online` does not enable network tools (`allowed_network` stays false).
- No API keys, tokens, or credentials are read or stored by this loop.
- Path escapes fail closed, including sibling prefixes (`tests/test_repair.py`).
- High-risk tool calls stop at `max_high_risk`.
- Unused declared packages (`pynacl`, `httpx`) are not a security control. Do not treat their presence as encryption or an HTTP client.

Report issues against https://github.com/beyond-repair/sunder. Do not file production-incident claims for this sketch.
