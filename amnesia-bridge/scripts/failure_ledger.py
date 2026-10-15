#!/usr/bin/env python3
"""
Amnesia Bridge: Negative Knowledge Ledger CLI
Tracks failed approaches, dead ends, and prohibited actions to prevent
agents from thrashing or repeating mistakes across long sessions.
"""

import os
import sys
import argparse
import re
from datetime import datetime
from pathlib import Path

DEFAULT_GRAVEYARD_PATH = Path(".agents/FAILURE_GRAVEYARD.md")
FALLBACK_GRAVEYARD_PATH = Path("FAILURE_GRAVEYARD.md")

GRAVEYARD_TEMPLATE = """# 🪦 Negative Knowledge Ledger: The Failure Graveyard

> **CRITICAL RULE FOR ALL AGENTS**:
> Before attempting any non-trivial fix, library installation, configuration change, or architectural refactor, **YOU MUST READ THIS FILE**.
> If your intended approach is recorded below as a **DEAD END**, **DO NOT ATTEMPT IT AGAIN**. Pivot immediately to a different strategy.

---

## 🛑 Dead Ends & Failed Approaches

| ID | Category | Attempted Approach | Why It Failed / Error Signal | Forbidden Action / Rule | Date |
|---|---|---|---|---|---|
"""

def find_graveyard_file(root_dir: Path = None) -> Path:
    base = root_dir or Path.cwd()
    if (base / DEFAULT_GRAVEYARD_PATH).exists():
        return base / DEFAULT_GRAVEYARD_PATH
    if (base / FALLBACK_GRAVEYARD_PATH).exists():
        return base / FALLBACK_GRAVEYARD_PATH
    # Default target for creation
    return base / DEFAULT_GRAVEYARD_PATH

def init_graveyard(root_dir: Path = None, force: bool = False) -> Path:
    target = find_graveyard_file(root_dir)
    if target.exists() and not force:
        print(f"ℹ️ Graveyard already exists at: {target}")
        return target
    
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(GRAVEYARD_TEMPLATE)
    print(f"✅ Initialized Negative Knowledge Ledger at: {target}")
    return target

def parse_entries(graveyard_path: Path):
    if not graveyard_path.exists():
        return []

    entries = []
    with open(graveyard_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find markdown table rows
    # | ID | Category | Attempted Approach | Why It Failed / Error Signal | Forbidden Action / Rule | Date |
    row_pattern = re.compile(r"^\|\s*(`FAIL-\d+`|FAIL-\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|", re.MULTILINE)
    for match in row_pattern.finditer(content):
        entries.append({
            "id": match.group(1).replace("`", "").strip(),
            "category": match.group(2).strip(),
            "attempt": match.group(3).strip(),
            "error": match.group(4).strip(),
            "rule": match.group(5).strip(),
            "date": match.group(6).strip()
        })
    return entries

def get_next_id(entries) -> str:
    max_num = 0
    for e in entries:
        m = re.search(r"FAIL-(\d+)", e.get("id", ""))
        if m:
            max_num = max(max_num, int(m.group(1)))
    return f"FAIL-{max_num + 1:03d}"

def record_failure(category: str, attempt: str, error: str, rule: str, root_dir: Path = None):
    target = find_graveyard_file(root_dir)
    if not target.exists():
        init_graveyard(root_dir)

    entries = parse_entries(target)
    new_id = get_next_id(entries)
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Clean inputs to prevent breaking markdown table
    c_clean = category.replace("|", "/").strip()
    a_clean = attempt.replace("|", "/").strip()
    e_clean = error.replace("|", "/").strip()
    r_clean = rule.replace("|", "/").strip()

    new_row = f"| `{new_id}` | {c_clean} | {a_clean} | {e_clean} | **{r_clean}** | {date_str} |\n"

    with open(target, "r", encoding="utf-8") as f:
        content = f.read()

    # Insert right after the table header separator
    table_header = "|---|---|---|---|---|---|\n"
    if table_header in content:
        parts = content.split(table_header, 1)
        updated_content = parts[0] + table_header + new_row + parts[1]
    else:
        # Fallback append
        updated_content = content + "\n" + new_row

    with open(target, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"🪦 Recorded [{new_id}] in {target}:")
    print(f"   Category:  {category}")
    print(f"   Attempted: {attempt}")
    print(f"   Reason:    {error}")
    print(f"   Rule:      {rule}")
    return new_id

STOP_WORDS = {
    "the", "and", "for", "with", "from", "this", "that", "have", "were", "what",
    "when", "using", "tried", "into", "onto", "over", "under", "about", "your",
    "will", "some", "trying", "attempt", "make", "just", "want"
}

def check_approach(query: str, root_dir: Path = None):
    target = find_graveyard_file(root_dir)
    if not target.exists():
        print("ℹ️ No Failure Graveyard found. All paths clear.")
        return 0

    entries = parse_entries(target)
    if not entries:
        print("ℹ️ Graveyard is empty. No past dead ends recorded.")
        return 0

    clean_query = query.strip().lower()
    query_tokens = [t for t in re.findall(r"\w+", clean_query) if len(t) >= 2 and t not in STOP_WORDS]
    query_tokens_set = set(query_tokens)
    matches = []

    for entry in entries:
        attempt_lower = entry["attempt"].lower()
        error_lower = entry["error"].lower()
        rule_lower = entry["rule"].lower()
        id_lower = entry["id"].lower()
        full_text = f"{entry['category']} {attempt_lower} {error_lower} {rule_lower}".lower()

        matched_reasons = []

        # 1. Exact ID check
        if id_lower in clean_query:
            matched_reasons.append(f"ID {entry['id']}")

        # 2. Substring matching: query inside attempt/rule, or attempt phrase inside query
        if len(clean_query) >= 4:
            if clean_query in attempt_lower or clean_query in rule_lower or clean_query in full_text:
                matched_reasons.append(f"Direct phrase match '{query}'")
            elif any(len(phrase) >= 4 and phrase in clean_query for phrase in re.split(r"[,;:\-–—]+", attempt_lower)):
                matched_reasons.append("Attempt phrase match")

        # 3. Token overlap matching
        entry_tokens = set(re.findall(r"\w+", full_text))
        overlap = query_tokens_set.intersection(entry_tokens)
        sig_tokens = {t for t in overlap if t not in STOP_WORDS}

        # If query is short (1-2 words), 1 significant match is enough; otherwise require >= 2
        min_tokens = 1 if len(query_tokens) <= 2 else 2
        if len(sig_tokens) >= min_tokens:
            matched_reasons.append(f"Keywords: {', '.join(sorted(sig_tokens))}")

        if matched_reasons:
            matches.append((entry, matched_reasons))

    if matches:
        print(f"\n🚨 WARNING: Found {len(matches)} potential dead end(s) matching your approach!\n")
        for entry, reasons in matches:
            print(f"❌ Match on [{entry['id']}] ({'; '.join(reasons)})")
            print(f"   Previous Attempt: {entry['attempt']}")
            print(f"   Why it Failed:    {entry['error']}")
            print(f"   FORBIDDEN RULE:   {entry['rule']}\n")
        return len(matches)
    else:
        print(f"✅ Approach check passed. No matching dead ends found for: '{query}'")
        return 0

def export_context(root_dir: Path = None, max_entries: int = 10):
    target = find_graveyard_file(root_dir)
    if not target.exists():
        return

    entries = parse_entries(target)
    if not entries:
        return

    print("### 🛑 ACTIVE AGENT CONSTRAINTS (From Failure Graveyard)\n")
    print("Do NOT attempt these proven dead ends:")
    for entry in entries[:max_entries]:
        print(f"- **[{entry['id']}] {entry['attempt']}**: {entry['rule']} *(Failed because: {entry['error']})*")
    print("")

def summarize_graveyard(root_dir: Path = None):
    target = find_graveyard_file(root_dir)
    if not target.exists():
        print("No Failure Graveyard found.")
        return

    entries = parse_entries(target)
    print(f"\n🪦 Failure Graveyard Summary: {target}")
    print(f"Total Recorded Dead Ends: {len(entries)}")

    categories = {}
    for e in entries:
        cat = e.get("category", "General")
        categories[cat] = categories.get(cat, 0) + 1

    print("\nBreakdown by Category:")
    for cat, count in categories.items():
        print(f"  • {cat}: {count}")

    if entries:
        print("\nMost Recent Entries:")
        for e in entries[:5]:
            print(f"  - [{e['id']}] {e['attempt']} -> {e['rule']}")
    print("")

def main():
    parser = argparse.ArgumentParser(description="Amnesia Bridge Negative Knowledge Ledger CLI")
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new FAILURE_GRAVEYARD.md")
    init_parser.add_argument("--dir", default=None, help="Root directory")
    init_parser.add_argument("--force", action="store_true", help="Overwrite if exists")

    # record
    rec_parser = subparsers.add_parser("record", help="Record a failed approach")
    rec_parser.add_argument("--category", "-c", required=True, help="Category (e.g. Dependency, API, Refactor, Config)")
    rec_parser.add_argument("--attempt", "-a", required=True, help="What was attempted")
    rec_parser.add_argument("--error", "-e", required=True, help="Why it failed or error message")
    rec_parser.add_argument("--rule", "-r", required=True, help="Prohibited action / rule for future agents")
    rec_parser.add_argument("--dir", default=None, help="Root directory")

    # check
    chk_parser = subparsers.add_parser("check", help="Check candidate action against past failures")
    chk_parser.add_argument("query", help="Candidate approach or description to test")
    chk_parser.add_argument("--dir", default=None, help="Root directory")

    # export-context
    exp_parser = subparsers.add_parser("export-context", help="Export compact prompt injection of dead ends")
    exp_parser.add_argument("--dir", default=None, help="Root directory")
    exp_parser.add_argument("--limit", type=int, default=10, help="Max entries to export")

    # summary
    sum_parser = subparsers.add_parser("summary", help="Show statistics of dead ends")
    sum_parser.add_argument("--dir", default=None, help="Root directory")

    args = parser.parse_args()

    if args.command == "init":
        init_graveyard(Path(args.dir) if args.dir else None, force=args.force)
    elif args.command == "record":
        record_failure(args.category, args.attempt, args.error, args.rule, Path(args.dir) if args.dir else None)
    elif args.command == "check":
        sys.exit(1 if check_approach(args.query, Path(args.dir) if args.dir else None) > 0 else 0)
    elif args.command == "export-context":
        export_context(Path(args.dir) if args.dir else None, max_entries=args.limit)
    elif args.command == "summary":
        summarize_graveyard(Path(args.dir) if args.dir else None)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
