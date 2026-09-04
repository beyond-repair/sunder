<div align="center">

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███████╗██╗   ██╗███╗   ██╗██████╗ ███████╗██████╗         ║
║   ██╔════╝██║   ██║████╗  ██║██╔══██╗██╔════╝██╔══██╗        ║
║   ███████╗██║   ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝        ║
║   ╚════██║██║   ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗        ║
║   ███████║╚██████╔╝██║ ╚████║██████╔╝███████╗██║  ██║        ║
║   ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝        ║
║                                                              ║
║         ＳＣＡＮ  →  ＳＮＡＰ  →  ＳＵＮＤＥＲ                ║
╚══════════════════════════════════════════════════════════════╝
```

# SUNDER

### Local-first autonomous coding agent  
**You are not the hero. You are the cold boot.**

**THE CITY WRITES ITS OWN REALITY.**  
**YOU JUST EDIT IT.**

[![ACTIVE](https://img.shields.io/badge/●_ACTIVE-a855f7?style=for-the-badge&labelColor=0f0f23)](https://github.com/beyond-repair/sunder)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-22d3ee?style=for-the-badge&labelColor=0f0f23)](#)
[![Offline](https://img.shields.io/badge/network__access-FALSE_by_default-ef4444?style=for-the-badge&labelColor=0f0f23)](#)
[![License](https://img.shields.io/badge/License-MIT-a855f7?style=for-the-badge&labelColor=0f0f23)](LICENSE)

```
STABILITY  ████████████████░░░░░░░░  72%
ALERT      ░░░░░░░░░░░░░░░░░░░░░░░░  18%
```

</div>

---

## ▌ Why SUNDER exists

Cursor feels magical because the AI lives *inside* the editor.  
Auto-GPT felt alive because it could chain tools toward a goal.

Most open-source agents still suffer from three fatal flaws:

1. **Amnesia** — context dies between sessions or is just RAG chunks.
2. **No authority boundary** — the agent can expand its own power.
3. **No reversible reality** — once it edits, the previous world is gone.

SUNDER fixes all three:

- **Hyperspherical VSA memory** (FHRR) — compositional, invertible, offline project memory.
- **Constitutional Gate** — every tool call is fail-closed. Network and high-risk actions require explicit authority.
- **Version Forking** — SNAP a parallel reality of the codebase, experiment, then SUNDER (commit or discard).

---

## ▌ The Loop

```text
  ┌─────────┐
  │  SCAN   │  Read the current reality (files, git, memory)
  └────┬────┘
       ▼
  ┌─────────┐
  │  SNAP   │  Create a parallel version-fork of state
  └────┬────┘
       ▼
  ┌─────────┐
  │ SUNDER  │  Apply changes, merge, or discard the fork
  └─────────┘
```

---

## ▌ Tools

| # | Tool | Function |
|:-:|:----:|----------|
| 1 | **SCAN** | Inspect project + VSA memory |
| 2 | **SNAP** | Fork current reality |
| 3 | **SPIKE** | High-risk action (still gated) |
| 4 | **ANCHOR** | Pin a stable checkpoint |
| 5 | **SUNDER** | Commit or discard the fork |

---

## ▌ Quick Start

```bash
git clone https://github.com/beyond-repair/sunder.git
cd sunder
pip install -r requirements.txt
python -m sunder "Refactor the authentication module and add tests"
```

---

## ▌ Architecture (honest)

```text
User Goal
   │
   ▼
┌──────────────────┐
│  Supervisor LLM  │  (local or gated remote)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────────┐
│  VSA Memory      │◄───►│  Constitutional Gate │
│  (FHRR project   │     │  (fail-closed tools) │
│   graph)         │     └─────────────────────┘
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Version Forks   │  SNAP → experiment → SUNDER
└──────────────────┘
```

This is not another thin wrapper around an API.  
It is a sovereign runtime for code.

---

<div align="center">

```
YOU WERE HERE BEFORE.
VERSION 17 FAILED.
DO NOT TRUST SABLE.
THE CITY REMEMBERS.
```

**REWRITE · BUILD · TRANSCEND**

[Atomic Dream Labs](https://github.com/beyond-repair)

</div>
