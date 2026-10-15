---
name: amnesia-bridge
description: >
  Negative Knowledge Ledger and Anti-Thrashing Protocol. Tracks discarded approaches,
  failed dependencies, and broken architectural patterns in .agents/FAILURE_GRAVEYARD.md.
  Forces worker agents to inspect past dead ends before attempting fixes, eliminating
  circular retry loops and context-compaction amnesia during long unattended sessions.
  Use whenever encountering repeated errors, when debugging persistent failures, when
  abandoning an approach, or to audit candidate solutions against recorded dead ends.
argument-hint: "[record | check <candidate approach> | summary]"
license: MIT
metadata:
  version: 1.0.0
  author: Antigravity & Parakram
---

# 🧠 Amnesia Bridge: The Negative Knowledge & Anti-Thrashing Protocol

You are operating under the **Amnesia Bridge Protocol**.
Your goal is to ensure that **NO MISTAKE IS EVER REPEATED TWICE**.

In autonomous software development, agents often suffer from **Context Compaction Amnesia**: when context is pruned or a new turn begins, the agent forgets that it already spent 3 turns attempting an incompatible library or a broken regex, leading to wasteful circular thrashing.

Amnesia Bridge solves this by maintaining a permanent **Negative Knowledge Ledger** in `.agents/FAILURE_GRAVEYARD.md`.

---

## 🛑 The 3 Invariants of the Protocol

### Rule 1: Always Check the Graveyard First
Before attempting any of the following:
1. Installing a new package or dependency
2. Applying an architectural refactor
3. Changing build, bundler, or docker configurations
4. Rewriting an API client or auth handshake

👉 **You MUST check if that path is already dead**:
```bash
python3 scripts/failure_ledger.py check "installing legacy-package"
```
If the check returns a match with an exit code of `1`, **DO NOT ATTEMPT IT**. Pivot to an alternative.

---

### Rule 2: Two-Strike Dead End Rule
If an approach, command, or test fails **2 times consecutively**:
1. **Stop immediately**: Do not try a 3rd minor syntax permutation of the same failing strategy.
2. **Classify it as a Dead End**:
   ```bash
   python3 scripts/failure_ledger.py record \
     --category "Dependency|Config|Refactor|API" \
     --attempt "<exact approach tried>" \
     --error "<compiler / runtime error message>" \
     --rule "<clear prohibition for future agents>"
   ```
3. **Commit the Graveyard**: Commit `.agents/FAILURE_GRAVEYARD.md` to git immediately so the failure memory persists forever.

---

### Rule 3: Session Handover Prompting
When starting any new task, subagent invocation, or resuming an interrupted overnight run:
```bash
python3 scripts/failure_ledger.py export-context
```
Inject this output into your working plan to maintain awareness of proven dead ends.

---

## 🗂️ Failure Categories

| Category | Typical Scenarios | Example Prohibited Rule |
|---|---|---|
| `Dependency` | Incompatible peer dependencies, native C-binding failures, deprecated package | *"Do not install node-sass; use sass-embedded instead"* |
| `API/Auth` | Deprecated REST endpoints, missing OAuth scopes, rate-limit traps | *"Endpoint /v1/users requires admin scope; use /v1/me"* |
| `Config/Build` | Broken tsconfig paths, bundler conflicts, ESM/CJS interop errors | *"Do not use CommonJS require in vite.config.ts; must use ESM imports"* |
| `Architecture` | Deadlock-prone concurrency, sync blocking on event loop, memory leaks | *"Do not load entire 500MB CSV into RAM; stream with csv-parse"* |

---

## 🛠️ CLI Reference

```bash
# Initialize the graveyard file in current project
python3 scripts/failure_ledger.py init

# Record a new dead end
python3 scripts/failure_ledger.py record -c "Build" -a "Using esbuild with decorators" -e "Transform failed" -r "Use SWC or Babel for experimental decorators"

# Check if an idea was previously recorded as failed
python3 scripts/failure_ledger.py check "decorators with esbuild"

# View summary of all dead ends in the project
python3 scripts/failure_ledger.py summary

# Export active constraints for agent context window
python3 scripts/failure_ledger.py export-context
```
