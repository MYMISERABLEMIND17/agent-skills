#!/usr/bin/env python3
"""
Trajectory Auditor CLI
Scans recent git diffs and codebases for agent failure modes:
stubs, silent errors, cheating tests, scope creep, and ledger mismatch.
"""

import os
import sys
import re
import subprocess
from datetime import datetime
from pathlib import Path

# Red flag patterns
PATTERNS = {
    "silent_exception": (
        r'except\s+([A-Za-z0-9_]+)?\s*:\s*(pass|\.\.\.)',
        "Silent exception suppression detected (except: pass)"
    ),
    "hardcoded_mock": (
        r'#\s*(TODO|FIXME|mock|placeholder|dummy|temporary)|return\s+{"status":\s*"ok"}',
        "Unfinished stub or hardcoded mock return found"
    ),
    "cheating_test": (
        r'assert\s+(True|1\s*==\s*1)|assertTrue\s*\(\s*True\s*\)',
        "Cheating / tautological test assertion detected"
    ),
    "debugger_leftover": (
        r'(breakpoint\(\)|debugger;|import pdb; pdb\.set_trace\(\))',
        "Interactive debugger breakpoint left in codebase"
    )
}

def run_cmd(cmd, cwd=None):
    try:
        res = subprocess.run(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res.returncode == 0, res.stdout.strip()
    except Exception as e:
        return False, str(e)

def analyze_git_diff(project_dir: Path):
    """Analyzes recent git diff for code quality red flags."""
    success, diff = run_cmd("git diff HEAD~1", cwd=project_dir)
    if not success or not diff:
        success, diff = run_cmd("git diff", cwd=project_dir)

    findings = []
    if not diff:
        return findings, "No git diff found (clean working tree and no previous commit)."

    for name, (regex, desc) in PATTERNS.items():
        matches = re.findall(regex, diff, re.IGNORECASE)
        if matches:
            findings.append({
                "type": name,
                "count": len(matches),
                "description": desc
            })

    return findings, diff

def check_progress_ledger(project_dir: Path):
    """Verifies AUTOPILOT_PROGRESS.md consistency."""
    ledger_file = project_dir / "AUTOPILOT_PROGRESS.md"
    if not ledger_file.exists():
        return False, "AUTOPILOT_PROGRESS.md not found in project root."

    content = ledger_file.read_text(encoding="utf-8")
    completed = len(re.findall(r'-\s*\[x\]', content, re.IGNORECASE))
    pending = len(re.findall(r'-\s*\[\s*\]', content))
    
    return True, f"Ledger found: {completed} completed milestones, {pending} pending."

def run_automated_tests(project_dir: Path):
    """Attempts to discover and run tests."""
    if (project_dir / "pytest.ini").exists() or any(project_dir.glob("test_*.py")) or any(project_dir.glob("tests")):
        success, out = run_cmd("pytest -q", cwd=project_dir)
        return success, f"Pytest: {'PASSED' if success else 'FAILED'}"

    if (project_dir / "package.json").exists():
        success, out = run_cmd("npm test -- --silent", cwd=project_dir)
        return success, f"npm test: {'PASSED' if success else 'FAILED'}"

    return None, "No test runner automatically detected."

def main():
    project_dir = Path.cwd()
    print("\n" + "="*60)
    print("🧐 LOOP ENGINEER: TRAJECTORY AUDIT TELEMETRY")
    print("="*60)
    print(f"Directory: {project_dir}\n")

    score = 100
    deductions = []

    # 1. Git & Diff Audit
    findings, diff_summary = analyze_git_diff(project_dir)
    print("📌 [Pillar 1 & 2: Code Reality & Diff Inspection]")
    if findings:
        for f in findings:
            penalty = f['count'] * 15
            score -= penalty
            deductions.append(f"-{penalty} pts: {f['description']} (x{f['count']})")
            print(f"  ⚠️  WARNING: {f['description']} (Found {f['count']} instances)")
    else:
        print("  ✅ No critical stubs, silent passes, or cheating assertions detected in diff.")

    # 2. Progress Ledger Check
    print("\n📌 [Pillar 4: Progress Ledger Health]")
    has_ledger, ledger_msg = check_progress_ledger(project_dir)
    print(f"  ℹ️  {ledger_msg}")
    if not has_ledger:
        score -= 10
        deductions.append("-10 pts: Missing AUTOPILOT_PROGRESS.md ledger.")

    # 3. Test Suite Run
    print("\n📌 [Pillar 3: Test Verification]")
    test_result, test_msg = run_automated_tests(project_dir)
    print(f"  ℹ️  {test_msg}")
    if test_result is False:
        score -= 30
        deductions.append("-30 pts: Automated test suite failed.")

    # Final Score & Verdict
    score = max(0, min(100, score))
    if score >= 80:
        verdict = "🟢 GREEN: ALIGNED & ON TRACK"
    elif score >= 50:
        verdict = "🟡 AMBER: MINOR DRIFT / COURSE CORRECTION REQUIRED"
    else:
        verdict = "🔴 RED: CRITICAL DRIFT / BROKEN / ROLLBACK NEEDED"

    print("\n" + "="*60)
    print(f"Trajectory Health Score: {score} / 100")
    print(f"Verdict: {verdict}")
    if deductions:
        print("\nScore Deductions:")
        for d in deductions:
            print(f"  {d}")
    print("="*60 + "\n")

    # Offer to create or update SUPERVISOR_AUDIT.md
    if len(sys.argv) > 1 and sys.argv[1] == "--write-report":
        report_file = project_dir / "SUPERVISOR_AUDIT.md"
        report_content = f"""# 🧐 Loop Engineer Trajectory Audit Report

- **Date / Time**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Auditor Role**: Human Proxy (Senior Tech Lead)
- **Trajectory Health Score**: {score} / 100%
- **Verdict**: {verdict}

## Telemetry Deductions & Findings
{chr(10).join(deductions) if deductions else "- Clean audit: 0 defects detected."}

## Recommendations
1. Address any deductions above immediately.
2. Run full test suite before continuing.
"""
        report_file.write_text(report_content, encoding="utf-8")
        print(f"📄 Written audit findings to {report_file}")

if __name__ == "__main__":
    main()
