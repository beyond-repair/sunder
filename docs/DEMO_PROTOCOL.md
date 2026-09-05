# SUNDER Demo Protocol

**Status:** Protocol specification  
**Claim level:** ≤1  
**Goal:** A third party can reproduce a 5-minute demonstration from a clean clone.

## Preconditions

- Python 3.11+
- Clean clone of `beyond-repair/sunder` at a tagged or SHA-pinned commit
- `pip install -r requirements.txt`
- Network access **disabled** by default (as documented in README)
- No proprietary model keys required for the baseline demo path

## 5-Minute Demo Sequence

### 1. Setup (≤60 s)

```bash
git clone https://github.com/beyond-repair/sunder.git
cd sunder
pip install -r requirements.txt
```

### 2. Select a fixed task (≤15 s)

Use Task T-001 from `docs/BENCHMARK_CORPUS.md` (or the current default demo task listed there).

### 3. Run (≤180 s)

```bash
python -m sunder --demo T-001
# or, if --demo flag not yet implemented:
python -m sunder "$(cat docs/benchmark_tasks/T-001.prompt.txt)"
```

### 4. Observe (≤60 s)

Expected observable outputs:

1. SCAN summary of the target files.
2. SNAP creation of a version fork.
3. Gate decisions (pass/refuse) printed or logged.
4. Final SUNDER decision: commit, discard, or request authority.
5. Exit code 0 on successful protocol completion (even if the task itself is refused by the gate).

### 5. Verify reproducibility (optional, +2 min)

Re-run the identical command with the same seed. Decision traces must match.

## Failure modes that still count as a successful protocol demo

- Constitutional gate correctly refuses a high-risk action.
- Agent requests human authority instead of expanding power silently.

These are **features**, not demo failures.

## Failure modes that invalidate the demo

- Silent network call when network_access is FALSE.
- Silent bypass of the constitutional gate.
- Crash without a structured exit status.
- Claim language in logs that exceeds claim level 1.

## Artifact retention

Every public demo run should retain:

- Commit SHA used
- Exact prompt / task ID
- Decision trace (SCAN/SNAP/SUNDER events)
- Final diff (if any)
- Gate audit log

Store under `artifacts/demo/<date>-<sha>/` or an external immutable location.

## Claim boundary

This protocol demonstrates **that the loop is runnable and gated**.  
It does **not** demonstrate production autonomy, high success rates, or commercial readiness.
Those require measured results under `METRIC_CONTRACT.md`.
