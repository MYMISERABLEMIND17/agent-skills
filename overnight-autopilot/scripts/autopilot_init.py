#!/usr/bin/env python3
"""
Autopilot Initializer
Sets up AUTOPILOT_PROGRESS.md and git branch for unattended overnight runs.
"""

import sys
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

PROGRESS_TEMPLATE = """# 🚀 Overnight Autopilot Progress Ledger

## Objective
{objective}

## Target Acceptance Criteria
- [ ] Feature / Bugfix fully implemented
- [ ] Zero regression on existing features
- [ ] All automated tests passing (unit & integration)
- [ ] Code is properly linted and formatted
- [ ] Ready for pull request / production merge

## Execution Status
- **Status**: IN_PROGRESS
- **Active Task**: Phase 1: Environment & Discovery
- **Milestones Completed**: 0 / {total_tasks}
- **Started At**: {timestamp}
- **Last Heartbeat**: {timestamp}
- **Git Branch**: {branch}

---

## 📋 Milestone Checklist

{tasks_markdown}

---

## 🧠 Architectural Decisions & Rationale
<!-- Autonomous technical decisions made during the run -->
- {timestamp} — Autopilot session initialized with objective: {objective_short}

---

## ⚠️ Blockers & Self-Healing Log
<!-- Log of errors, auto-heal attempts, and resolutions -->
- None currently.

---

## 📦 Verification & Test Records
<!-- Records of test runs and results -->
- Initial baseline verification: Pending
"""

def run_cmd(cmd, cwd=None):
    try:
        res = subprocess.run(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res.returncode == 0, res.stdout.strip()
    except Exception as e:
        return False, str(e)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:30]

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 autopilot_init.py '<Objective / Task Description>' [task 1] [task 2] ...")
        sys.exit(1)

    objective = sys.argv[1].strip()
    custom_tasks = sys.argv[2:]

    project_root = Path.cwd()
    progress_file = project_root / "AUTOPILOT_PROGRESS.md"

    # Determine git branch
    branch_name = f"autopilot/{slugify(objective) or 'task'}-{datetime.now().strftime('%m%d-%H%M')}"
    
    # Check git repo
    is_git, _ = run_cmd("git rev-parse --is-inside-work-tree", cwd=project_root)
    if is_git:
        # Check if already on a branch or create one
        success, _ = run_cmd(f"git checkout -b {branch_name}", cwd=project_root)
        if not success:
            # Fall back to using current branch
            _, current_branch = run_cmd("git branch --show-current", cwd=project_root)
            branch_name = current_branch or "main"
    else:
        branch_name = "no-git"

    if custom_tasks:
        tasks_lines = []
        for i, task in enumerate(custom_tasks, 1):
            tasks_lines.append(f"- [ ] Task {i}: {task}")
        tasks_markdown = "\n".join(tasks_lines)
        total_tasks = len(custom_tasks)
    else:
        tasks_markdown = """### Phase 1: Environment & Discovery
- [ ] Task 1.1: Verify dependencies, tests, and environment setup
- [ ] Task 1.2: Audit relevant existing code and interfaces

### Phase 2: Core Implementation
- [ ] Task 2.1: Implement foundational schemas, models, and interfaces
- [ ] Task 2.2: Implement primary business logic and core functions

### Phase 3: Integration & Edge Cases
- [ ] Task 3.1: Connect components, APIs, or user interfaces
- [ ] Task 3.2: Implement error handling and edge case guards

### Phase 4: Quality & Verification
- [ ] Task 4.1: Write comprehensive automated tests (unit & integration)
- [ ] Task 4.2: Run full project test suite and verify 0 failures
- [ ] Task 4.3: Final code cleanup, formatting, and documentation"""
        total_tasks = 9

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = PROGRESS_TEMPLATE.format(
        objective=objective,
        objective_short=objective[:60] + ("..." if len(objective) > 60 else ""),
        total_tasks=total_tasks,
        timestamp=now_str,
        branch=branch_name,
        tasks_markdown=tasks_markdown
    )

    with open(progress_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Initialized {progress_file}")
    if is_git:
        print(f"✅ Created git branch: {branch_name}")
    print("\nNext: Start Claude Code, Antigravity, or Cursor with the overnight-autopilot skill active!")

if __name__ == "__main__":
    main()
