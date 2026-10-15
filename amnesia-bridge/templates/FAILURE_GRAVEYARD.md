# 🪦 Negative Knowledge Ledger: The Failure Graveyard

> **CRITICAL RULE FOR ALL AGENTS**:
> Before attempting any non-trivial fix, library installation, configuration change, or architectural refactor, **YOU MUST READ THIS FILE**.
> If your intended approach is recorded below as a **DEAD END**, **DO NOT ATTEMPT IT AGAIN**. Pivot immediately to a different strategy.

---

## 🛑 Dead Ends & Failed Approaches

| ID | Category | Attempted Approach | Why It Failed / Error Signal | Forbidden Action / Rule | Date |
|---|---|---|---|---|---|
| `FAIL-001` | *Example: Dependency* | `npm install legacy-pkg` | Incompatible with React 19 peer deps; engine mismatch | Do not install legacy-pkg; use modern alternative or native fetch | 2026-10-15 |

---

## 📋 Failure Analysis & Architectural Invariants

### 1. Incompatible Technologies / Libraries
- *(Record libraries, APIs, or versions that have been proven incompatible with this repo)*

### 2. Discarded Architecture / Patterns
- *(Record patterns that were tried and failed due to project constraints)*

### 3. Environment & Runtime Quirks
- *(Record machine-specific, OS-specific, or network constraints)*

---

## ⚡ How to Add Entries
Use the CLI tool:
```bash
python3 scripts/failure_ledger.py record \
  --category "Dependency" \
  --attempt "Tried running webpack without ts-loader" \
  --error "Module parse failed: Unexpected token" \
  --rule "Always use ts-loader or migrate to esbuild"
```
Or manually append a row to the table above following the format.
