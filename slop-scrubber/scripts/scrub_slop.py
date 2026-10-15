#!/usr/bin/env python3
"""
Slop Scrubber CLI: Code Hygiene and Cruft Cleaner
Scans and cleans git diffs and files for AI slop: debug statements,
zombie stubs, trailing whitespace, breakpoints, and merge conflicts.
"""

import os
import sys
import argparse
import json
import re
import subprocess
from pathlib import Path

DEFAULT_RULES = {
    "general": [
        {
            "name": "debugger_breakpoint",
            "regex": r"^\s*(?:debugger\s*;?|breakpoint\s*\(\s*\)|pdb\.set_trace\s*\(\s*\)|import\s+pdb\s*(?:;\s*pdb\.set_trace\s*\(\s*\))?)\s*$",
            "severity": "CRITICAL",
            "message": "Interactive debugger or breakpoint left in code",
            "autoclean": False
        },
        {
            "name": "merge_conflict_marker",
            "regex": r"^(<<<<<<<|=======|>>>>>>>)",
            "severity": "CRITICAL",
            "message": "Git merge conflict marker left in file",
            "autoclean": False
        },
        {
            "name": "temporary_todo",
            "regex": r"^\s*(?://|#|/\*)\s*(TODO|FIXME):?\s*(remove|temporary|delete|cleanup|hack|dummy)",
            "severity": "WARNING",
            "message": "Temporary TODO or cleanup stub flagged for deletion",
            "autoclean": False
        }
    ],
    "python": {
        "extensions": [".py"],
        "rules": [
            {
                "name": "python_debug_print",
                "regex": r"^\s*print\s*\(\s*[\"'].*?(?:debug|>>>|###|temp|asdf|here\s*\d*|\bval\s*:).*?[\"'].*?\)",
                "severity": "WARNING",
                "message": "Temporary debug print() statement",
                "autoclean": True
            },
            {
                "name": "python_silent_suppression",
                "regex": r"^[ \t]*except(?:\s+[A-Za-z0-9_]+)?\s*:\s*(?:pass|\.\.\.)\s*$",
                "severity": "CRITICAL",
                "message": "Silent exception suppression (except: pass / ...)",
                "autoclean": False
            },
            {
                "name": "python_fake_return_mock",
                "regex": r"^\s*return\s+\{\s*[\"']status[\"']\s*:\s*[\"']ok[\"']\s*\}\s*$",
                "severity": "WARNING",
                "message": "Hardcoded fake return mock",
                "autoclean": False
            }
        ]
    },
    "javascript": {
        "extensions": [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"],
        "rules": [
            {
                "name": "js_console_log",
                "regex": r"^\s*console\.(log|debug|info|warn|error)\s*\(.*?\);?",
                "severity": "WARNING",
                "message": "Console log statement left in code",
                "autoclean": True
            },
            {
                "name": "js_alert",
                "regex": r"^\s*alert\s*\(.*?\);?",
                "severity": "CRITICAL",
                "message": "Browser alert() left in frontend code",
                "autoclean": True
            }
        ]
    },
    "go": {
        "extensions": [".go"],
        "rules": [
            {
                "name": "go_fmt_print",
                "regex": r"^\s*fmt\.(Println|Printf|Print)\s*\(.*?\)",
                "severity": "WARNING",
                "message": "Temporary fmt.Print debug statement",
                "autoclean": True
            }
        ]
    },
    "rust": {
        "extensions": [".rs"],
        "rules": [
            {
                "name": "rust_dbg_macro",
                "regex": r"^\s*(?:dbg!\s*\(|println!\s*\(\s*\"debug)",
                "severity": "WARNING",
                "message": "Rust dbg! or debug println! macro left in code",
                "autoclean": True
            }
        ]
    }
}

def load_rules(custom_rules_path: str = None) -> dict:
    if custom_rules_path and Path(custom_rules_path).exists():
        try:
            with open(custom_rules_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load custom rules ({e}), falling back to built-in rules.")
    return DEFAULT_RULES

CODE_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".go", ".rs", ".html", ".css", ".java", ".c", ".cpp", ".php", ".rb"
}

def get_git_modified_files(cwd: Path = None) -> list:
    """Returns list of modified or untracked code files according to git."""
    try:
        res = subprocess.run("git status --porcelain", shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            return []
        files = []
        for line in res.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                file_path = parts[1].strip()
                # Resolve rename if R status
                if " -> " in file_path:
                    file_path = file_path.split(" -> ")[1].strip()
                full_path = (cwd or Path.cwd()) / file_path
                if full_path.is_file() and full_path.suffix.lower() in CODE_EXTS:
                    files.append(full_path)
        return files
    except Exception:
        return []

def get_all_code_files(root: Path, max_depth: int = 5) -> list:
    ignored_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next", ".cache"}
    found = []
    for p in root.rglob("*"):
        if any(part in ignored_dirs for part in p.parts):
            continue
        if p.is_file() and p.suffix.lower() in CODE_EXTS:
            found.append(p)
    return found

def get_applicable_rules(file_path: Path, rules_config: dict) -> list:
    applicable = list(rules_config.get("general", []))
    ext = file_path.suffix.lower()
    for lang, conf in rules_config.items():
        if lang == "general" or not isinstance(conf, dict):
            continue
        if ext in conf.get("extensions", []):
            applicable.extend(conf.get("rules", []))
    return applicable

def scan_file(file_path: Path, rules_config: dict) -> list:
    findings = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception as e:
        return [{"line": 0, "severity": "ERROR", "message": f"Could not read file: {e}", "rule": "io_error"}]

    rules = get_applicable_rules(file_path, rules_config)

    for idx, line in enumerate(lines, 1):
        # Check trailing whitespace
        if line.rstrip("\r\n") != line.rstrip():
            findings.append({
                "file": str(file_path),
                "line": idx,
                "severity": "INFO",
                "message": "Trailing whitespace detected",
                "rule": "trailing_whitespace",
                "snippet": line.strip()
            })

        for r in rules:
            regex = r["regex"]
            if re.search(regex, line, re.IGNORECASE):
                findings.append({
                    "file": str(file_path),
                    "line": idx,
                    "severity": r["severity"],
                    "message": r["message"],
                    "rule": r["name"],
                    "snippet": line.strip()
                })

    # Multiline syntax checks
    full_text = "".join(lines)
    ext = file_path.suffix.lower()
    if ext == ".py":
        # Multiline silent exception: except...:\n pass
        multiline_except = re.compile(r"^[ \t]*except(?:\s+[A-Za-z0-9_]+)?\s*:\s*\n[ \t]*(?:pass|\.\.\.)\s*$", re.MULTILINE)
        for m in multiline_except.finditer(full_text):
            line_num = full_text[:m.start()].count("\n") + 1
            findings.append({
                "file": str(file_path),
                "line": line_num,
                "severity": "CRITICAL",
                "message": "Silent exception suppression (multiline except: pass / ...)",
                "rule": "python_silent_suppression_multiline",
                "snippet": m.group(0).strip()
            })
    elif ext in (".js", ".jsx", ".ts", ".tsx"):
        # Multiline empty catch: catch(...) {}
        empty_catch = re.compile(r"^[ \t]*catch(?:\s*\([^)]*\))?\s*\{\s*\}", re.MULTILINE)
        for m in empty_catch.finditer(full_text):
            line_num = full_text[:m.start()].count("\n") + 1
            findings.append({
                "file": str(file_path),
                "line": line_num,
                "severity": "CRITICAL",
                "message": "Empty catch block suppressing error without logging",
                "rule": "js_empty_catch",
                "snippet": m.group(0).strip()
            })

    # Check EOF newline
    if lines and not lines[-1].endswith("\n"):
        findings.append({
            "file": str(file_path),
            "line": len(lines),
            "severity": "INFO",
            "message": "Missing newline at end of file",
            "rule": "missing_eof_newline",
            "snippet": lines[-1].strip()
        })

    return findings

def clean_file(file_path: Path, rules_config: dict) -> int:
    """Cleans autocleanable slop and normalizes whitespace."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return 0

    rules = get_applicable_rules(file_path, rules_config)
    autoclean_rules = [r for r in rules if r.get("autoclean", False)]

    cleaned_lines = []
    removed_count = 0

    for line in lines:
        stripped_end = line.rstrip(" \t\r\n") + "\n"
        
        # Check if line should be removed
        should_remove = False
        for r in autoclean_rules:
            if re.search(r["regex"], line, re.IGNORECASE):
                should_remove = True
                removed_count += 1
                break

        if not should_remove:
            cleaned_lines.append(stripped_end)

    # Collapse excessive blank lines
    compacted = []
    consecutive_empty = 0
    for l in cleaned_lines:
        if l.strip() == "":
            consecutive_empty += 1
            if consecutive_empty <= 1:
                compacted.append("\n")
        else:
            consecutive_empty = 0
            compacted.append(l)

    content = "".join(compacted).strip() + "\n" if any(c.strip() for c in compacted) else ""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return removed_count

def run_scan(target_files: list, rules_config: dict) -> tuple:
    all_findings = []
    for fp in target_files:
        findings = scan_file(fp, rules_config)
        all_findings.extend(findings)
    return all_findings

def print_findings(findings: list):
    if not findings:
        print("✨ CLEAN! No AI slop or hygiene issues detected.")
        return

    severity_icons = {
        "CRITICAL": "🚨",
        "WARNING": "⚠️",
        "INFO": "ℹ️",
        "ERROR": "❌"
    }

    counts = {"CRITICAL": 0, "WARNING": 0, "INFO": 0}
    print(f"\n🔍 Found {len(findings)} hygiene item(s):\n")

    for f in findings:
        sev = f.get("severity", "INFO")
        counts[sev] = counts.get(sev, 0) + 1
        icon = severity_icons.get(sev, "•")
        print(f"{icon} [{sev}] {f['file']}:{f['line']}")
        print(f"   Issue:   {f['message']}")
        if f.get("snippet"):
            print(f"   Snippet: {f['snippet']}")
        print("")

    print("--------------------------------------------------")
    print(f"Summary: {counts.get('CRITICAL', 0)} Critical, {counts.get('WARNING', 0)} Warnings, {counts.get('INFO', 0)} Info")
    print("--------------------------------------------------")

def main():
    parser = argparse.ArgumentParser(description="Slop Scrubber CLI")
    subparsers = parser.add_subparsers(dest="command", help="Subcommand")

    # scan
    scan_p = subparsers.add_parser("scan", help="Scan files or git diff for slop")
    scan_p.add_argument("--diff", action="store_true", help="Scan only git-modified files (default)")
    scan_p.add_argument("--all", action="store_true", help="Scan all files in directory")
    scan_p.add_argument("--file", "-f", help="Scan specific file")
    scan_p.add_argument("--rules", help="Path to custom SLOP_RULES.json")

    # clean
    clean_p = subparsers.add_parser("clean", help="Auto-clean removable slop and whitespace")
    clean_p.add_argument("--diff", action="store_true", help="Clean only git-modified files (default)")
    clean_p.add_argument("--all", action="store_true", help="Clean all files in directory")
    clean_p.add_argument("--file", "-f", help="Clean specific file")
    clean_p.add_argument("--rules", help="Path to custom SLOP_RULES.json")

    # verify
    ver_p = subparsers.add_parser("verify", help="Strict pre-commit check (exits 1 if slop found)")
    ver_p.add_argument("--diff", action="store_true", help="Check only git-modified files (default)")
    ver_p.add_argument("--all", action="store_true", help="Check all files in directory")
    ver_p.add_argument("--file", "-f", help="Check specific file")
    ver_p.add_argument("--rules", help="Path to custom SLOP_RULES.json")

    args = parser.parse_args()
    rules_config = load_rules(getattr(args, "rules", None))

    # Determine files to inspect
    if getattr(args, "file", None):
        target_files = [Path(args.file)]
    elif getattr(args, "all", None):
        target_files = get_all_code_files(Path.cwd())
    else:
        # Default is --diff
        target_files = get_git_modified_files(Path.cwd())
        if not target_files:
            # Fallback to scanning current dir if not in git repo or clean
            target_files = get_all_code_files(Path.cwd())

    if args.command in ("scan", None):
        findings = run_scan(target_files, rules_config)
        print_findings(findings)
    elif args.command == "clean":
        print(f"🧹 Scrubbing slop across {len(target_files)} file(s)...")
        total_cleaned = 0
        for fp in target_files:
            removed = clean_file(fp, rules_config)
            if removed > 0:
                print(f"  • Removed {removed} slop item(s) in {fp}")
            total_cleaned += removed
        print(f"✅ Scrub complete! Cleaned {total_cleaned} statement(s) and normalized whitespace.")
    elif args.command == "verify":
        findings = run_scan(target_files, rules_config)
        critical_or_warn = [f for f in findings if f.get("severity") in ("CRITICAL", "WARNING")]
        if critical_or_warn:
            print_findings(critical_or_warn)
            print("\n❌ Verification Failed: Code contains unscrubbed slop or critical debug statements!")
            sys.exit(1)
        else:
            print("✅ Verification Passed: Zero critical AI slop detected.")
            sys.exit(0)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
