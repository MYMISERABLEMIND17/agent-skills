# 🌙 Overnight Autopilot

**Autonomous, zero-interruption execution engine for Claude Code, Antigravity, and Cursor.**

Work all night unattended without hitting confirmation prompts, losing context memory, or stalling on minor errors.

---

## 🎯 What Problem Does This Solve?

Standard AI coding assistants are prompt-tuned to be conversational and cautious:
1. **The Permission Wall**: They constantly stop and ask: *"Should I run tests?", "Would you like me to install this package?", "Allow command `npm test`? [y/n]"*. If you go to sleep, the agent stops 3 minutes later.
2. **Context Window Amnesia**: Long tasks fill the context window. When the conversation compacts or resets, the agent forgets where it was and starts over or loops in circles.
3. **Fragile Error Handling**: If a test fails, the agent often freezes or asks: *"I encountered an error, what should I do?"*.

**Overnight Autopilot transforms your AI assistant into an autonomous lead engineer:**
- **Zero-Question Protocol**: Assumes implicit approval for all constructive development steps. Never asks rhetorical questions.
- **Disk-Based State Ledger (`AUTOPILOT_PROGRESS.md`)**: Progress is saved on disk. If the context window fills or restarts, the agent reads the ledger and immediately picks up the exact next task.
- **3-Strike Self-Healing**: Automatically parses stack traces and applies up to 3 diagnostic auto-fixes before deferring.
- **Atomic Git Checkpoints**: Commits every verified milestone so no work is ever lost.

---

## 🚀 Quick Setup & Installation

The skill and tooling are already installed on your system! If you ever need to re-run the installer:

```bash
cd "/home/tomar_parakram/Desktop/MY RAN IDEAS/overnight-autopilot"
./install.sh
```

This automatically configures:
- **Antigravity / Gemini CLI**: `~/.gemini/config/skills/overnight-autopilot/SKILL.md`
- **Claude Code**: `~/.claude/skills/overnight-autopilot/SKILL.md`
- **Global Terminal Command**: `autopilot` in `~/.local/bin`

---

## 💡 How to Use by Platform

### 1. In Claude Code

#### Option A: Interactive Chat (Zero Interruptions)
Launch Claude Code with permission bypass:
```bash
claude --dangerously-skip-permissions
```
Then prompt Claude:
```text
Activate the overnight-autopilot skill and build [your feature description].
```
Claude will initialize `AUTOPILOT_PROGRESS.md`, create a git branch, and work through the task list without pausing to ask for permission.

#### Option B: Terminal Overnight Daemon (Runs All Night in Background)
If you want to go to sleep and let your terminal run continuous loops until done:
```bash
cd /path/to/your/project
autopilot init "Build complete user authentication and JWT middleware"
autopilot run --agent claude
```
This daemon will invoke Claude turn-by-turn until every single milestone in `AUTOPILOT_PROGRESS.md` is marked `[x]`!

---

### 2. In Antigravity / Gemini CLI

In Antigravity IDE or CLI, simply type:
```text
Activate overnight-autopilot and implement [your feature or task].
```
Antigravity automatically discovers `~/.gemini/config/skills/overnight-autopilot/SKILL.md` and applies the zero-interruption protocol and persistence engine.

---

### 3. In Cursor

1. Open your project in Cursor.
2. Run this command inside your project folder:
   ```bash
   autopilot cursor
   ```
   *(This copies `.cursor/rules/overnight-autopilot.mdc` and `.cursorrules` into your project).*
3. In Cursor Settings:
   - Enable **Agent Mode** / Composer.
   - Set Terminal commands to **Auto-run** (Yolo mode).
4. In Composer / Chat, prompt:
   ```text
   Run in overnight-autopilot mode: build [your feature description].
   ```

---

## 📋 The Progress Ledger (`AUTOPILOT_PROGRESS.md`)

When active, the agent creates and continuously maintains an `AUTOPILOT_PROGRESS.md` ledger:

```markdown
# 🚀 Overnight Autopilot Progress Ledger

## Objective
Build complete user authentication and JWT middleware

## Execution Status
- Status: IN_PROGRESS
- Active Task: Phase 2: JWT generation & verification
- Milestones Completed: 3 / 8
- Git Branch: autopilot/auth-middleware

## 📋 Milestone Checklist
- [x] Task 1: Environment & dependency verification
- [x] Task 2: User schema & password hashing
- [ ] Task 3: JWT token issuance & refresh rotation
- [ ] Task 4: Auth middleware & protected routes
- [ ] Task 5: Automated test suite (unit + edge cases)
```

Every time a milestone finishes:
1. Tests are executed.
2. `[ ]` flips to `[x]`.
3. An atomic git commit is made (`git commit -m "autopilot: completed task 3"`).

---

## 🛠️ CLI Command Reference

| Command | Description |
| :--- | :--- |
| `autopilot init "<objective>"` | Creates `AUTOPILOT_PROGRESS.md` and a clean git branch. |
| `autopilot run` | Starts the autonomous loop daemon (auto-detects Claude / Antigravity). |
| `autopilot run --agent claude --max-turns 40` | Runs the loop using Claude Code for up to 40 turns. |
| `autopilot cursor` | Adds Cursor-specific rules to the current project. |

---

## 🛡️ Safety & Circuit Breakers

- **Read-Only / Test Validation**: Code is never considered done until automated tests pass with 0 errors.
- **Git Rollbacks**: If an approach fails after 3 auto-healing attempts, the agent resets to the last working commit and pivots to an alternative strategy instead of leaving broken code behind.
- **Max Turn Limits**: The daemon runner has a configurable turn cap (default 30) so you never get runaway token usage if a true physical blocker occurs.
