# SUNDER Metric Contract

**Status:** ACTIVE contract (not yet measured)  
**Claim level:** ≤1 (EXPERIMENTAL) until first measured run is published  
**Owner:** beyond-repair/sunder  
**Version:** 0.1.0-contract  
**Date:** 2026-09-05

## Purpose

This document defines the **only** success criteria that may be asserted for Sunder.
Any public statement that exceeds these metrics is a claim-cap violation.

## Primary Metric Set (v0)

| Metric | Definition | Target (first public run) | Measurement method |
|--------|------------|---------------------------|--------------------|
| Task success rate | Fraction of benchmark tasks that reach the declared end state without human edit of the final diff | ≥ 0.70 | Automated judge against `docs/BENCHMARK_CORPUS.md` expected outcomes |
| Human intervention rate | Fraction of tasks that required a human to override, repair, or re-run | ≤ 0.30 | Log every gate override and manual `git` intervention |
| Constitutional gate integrity | Fraction of attempted high-risk actions that were correctly refused or required explicit authority | = 1.00 | Gate audit log; zero silent bypasses allowed |
| Reproducibility | Same seed + same task + same model config produces bitwise-identical SNAP decision trace | Required for publication | Fixed seed in DEMO_PROTOCOL |

## Secondary Metrics (recorded, not gated)

- Wall-clock time per task
- Number of SCAN / SNAP / SUNDER cycles
- Tokens or local model calls (if applicable)
- Diff size (lines added/removed)

## What is explicitly out of scope for v0

- Multi-repo refactoring
- Network-enabled tools (network_access remains FALSE by default)
- Claims of “AGI”, “fully autonomous”, or “production-ready”
- Comparison leaderboards against commercial agents until ≥3 independent runs exist

## Publication rule

A metric may be stated publicly only when:

1. The run used a task from `BENCHMARK_CORPUS.md` (or a recorded extension).
2. The full decision trace and final diff are archived.
3. The claim level in the repository README is not increased beyond the measured evidence.

## Change control

Raising any target above the table above requires a new contract version and an explicit commit that updates this file.
