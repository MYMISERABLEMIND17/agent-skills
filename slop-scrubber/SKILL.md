---
name: slop-scrubber
description: >
  Code Hygiene and AI Slop Cleaner Protocol. Scans git diffs and modified files for
  temporary debug prints, console.logs, interactive breakpoints (debugger, pdb), merge
  conflict markers, silent exception suppressions (except: pass), fake mock return stubs,
  and trailing whitespace. Provides non-destructive scanning, strict pre-commit verification,
  and one-command automated scrubbing. Use before committing changes, during PR preparation,
  or whenever instructed to clean up slop, remove debug statements, or sanitize code.
argument-hint: "[scan | clean | verify]"
license: MIT
metadata:
  version: 1.0.0
  author: Antigravity & Parakram
---

# 🧹 Slop Scrubber: Code Hygiene & Cruft Sanitizer

You are operating under the **Slop Scrubber Protocol**.
Your goal is simple: **Ensure code diffs look like they were handcrafted by an obsessive Principal Engineer, not spat out by a rushed AI model.**

Autonomous coding agents frequently leave behind temporary scaffolding:
- Ad-hoc print statements (`console.log("here 1")`, `print("DEBUG: result")`)
- Dangerous breakpoints (`debugger;`, `breakpoint()`, `import pdb`)
- Silent error suppression (`except Exception: pass`)
- Formatting anomalies (trailing spaces, missing EOF newlines, double semicolons)

---

## 🔍 The 5 Slop Categories

| Category | Example Slop | Severity | Auto-Cleanable? |
|---|---|---|---|
| **Breakpoints** | `debugger;`, `breakpoint()`, `pdb.set_trace()` | 🚨 `CRITICAL` | ❌ Manual fix required |
| **Silent Suppressions** | `except Exception: pass`, `catch (e) {}` | 🚨 `CRITICAL` | ❌ Manual fix required |
| **Conflict Markers** | `<<<<<<< HEAD`, `=======`, `>>>>>>>` | 🚨 `CRITICAL` | ❌ Manual fix required |
| **Debug Statements** | `console.log(...)`, `print("val:", x)` | ⚠️ `WARNING` | ✅ Yes (`slop-scrubber clean`) |
| **Whitespace Cruft** | Trailing spaces, missing EOF newline | ℹ️ `INFO` | ✅ Yes (`slop-scrubber clean`) |

---

## ⚡ The Pre-Commit Hygiene Workflow

### Step 1: Scan Recent Changes
Before staging any commit, run a non-destructive scan against the modified files:
```bash
python3 scripts/scrub_slop.py scan --diff
```

### Step 2: Auto-Clean Scaffolding
Automatically strip out debug print statements and normalize trailing whitespace:
```bash
python3 scripts/scrub_slop.py clean --diff
```

### Step 3: Strict Pre-Commit Verification
Run strict verification. If critical items (like silent exception suppression or breakpoints) remain, the tool exits with code `1`:
```bash
python3 scripts/scrub_slop.py verify --diff
```

---

## 🛠️ CLI Reference

```bash
# Scan git modified files (default)
python3 scripts/scrub_slop.py scan

# Scan all tracked project files
python3 scripts/scrub_slop.py scan --all

# Scan a single file
python3 scripts/scrub_slop.py scan -f src/auth/service.ts

# Auto-clean debug logs and trailing spaces across changed files
python3 scripts/scrub_slop.py clean

# Verify clean state for CI / Git hooks
python3 scripts/scrub_slop.py verify
```

---

## 🤝 Pairing with Other Agent Skills

- **Pair with `overnight-autopilot`**: Runs automatically at the end of each completed task before generating the final git commit.
- **Pair with `loop-engineer`**: Supplies the raw code quality metrics needed for Pillar 2 (Code Reality vs AI Slop).
