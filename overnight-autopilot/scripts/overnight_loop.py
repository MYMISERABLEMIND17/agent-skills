#!/usr/bin/env python3
"""
Overnight Autopilot Loop Daemon
Runs Claude Code, Antigravity, or other CLI agents continuously until all tasks
in AUTOPILOT_PROGRESS.md are completed, without asking for permission.
"""

import os
import sys
import time
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

DEFAULT_CLAUDE_PROMPT = """You are operating under the 'overnight-autopilot' skill.
Read AUTOPILOT_PROGRESS.md. Continue executing the next pending tasks autonomously.
Follow the Zero-Interruption rule: do NOT ask for permission or prompt the user.
Implement the required code, run tests, ensure 0 errors, commit progress to git,
and update AUTOPILOT_PROGRESS.md. Stop only when ALL tasks are marked [x]."""

def parse_progress(file_path: Path):
    """Parses AUTOPILOT_PROGRESS.md for pending and completed tasks."""
    if not file_path.exists():
        return False, 0, 0, []

    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    pending = []
    completed = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- [ ]"):
            pending.append(stripped[5:].strip())
        elif stripped.lower().startswith("- [x]"):
            completed.append(stripped[5:].strip())

    is_complete = len(pending) == 0 and len(completed) > 0
    return is_complete, len(completed), len(pending), pending

def find_cli_agent():
    """Detects available AI CLI agents installed on the system."""
    for binary in ["claude", "agy", "gemini"]:
        try:
            res = subprocess.run(f"which {binary}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return binary
        except Exception:
            pass
    return None

def run_agent_turn(agent_bin: str, prompt: str, project_dir: Path, log_file: Path):
    """Executes a single agent turn with bypass flags."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*70}\n[{timestamp}] LAUNCHING TURN WITH {agent_bin.upper()}\n{'='*70}\n")

    if agent_bin == "claude":
        # Claude Code unattended execution with bypass
        cmd = [
            "claude",
            "--dangerously-skip-permissions",
            "-p", prompt
        ]
    elif agent_bin in ["agy", "gemini"]:
        cmd = [
            agent_bin,
            "-p", prompt
        ]
    else:
        raise ValueError(f"Unsupported agent binary: {agent_bin}")

    print(f"[{timestamp}] Running command: {' '.join(cmd[:2])} ...")
    
    with open(log_file, "a", encoding="utf-8") as log_f:
        process = subprocess.Popen(
            cmd,
            cwd=str(project_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Stream output to both terminal and log
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            log_f.write(line)
            log_f.flush()

        process.wait()
        return process.returncode

def main():
    parser = argparse.ArgumentParser(description="Overnight Autopilot Autonomous Loop Runner")
    parser.add_argument("--agent", choices=["claude", "agy", "gemini", "auto"], default="auto",
                        help="CLI agent to execute (default: auto-detect)")
    parser.add_argument("--max-turns", type=int, default=30,
                        help="Maximum autonomous turns before graceful exit (default: 30)")
    parser.add_argument("--cooldown", type=int, default=5,
                        help="Cooldown in seconds between turns (default: 5)")
    parser.add_argument("--prompt", type=str, default=DEFAULT_CLAUDE_PROMPT,
                        help="Custom instruction prompt to pass to the agent")
    args = parser.parse_args()

    project_dir = Path.cwd()
    progress_file = project_dir / "AUTOPILOT_PROGRESS.md"
    log_file = project_dir / "autopilot_run.log"

    print("\n" + "="*60)
    print("🌙 OVERNIGHT AUTOPILOT DAEMON STARTED")
    print("="*60)
    print(f"Project Directory: {project_dir}")
    print(f"Log File:          {log_file}")

    if not progress_file.exists():
        print(f"❌ Error: {progress_file} not found.")
        print("Run `python3 autopilot_init.py 'Your task'` first to initialize the ledger.")
        sys.exit(1)

    agent_bin = args.agent
    if agent_bin == "auto":
        agent_bin = find_cli_agent()
        if not agent_bin:
            print("❌ Error: No supported AI CLI found (checked: claude, agy, gemini).")
            print("Please ensure Claude Code or Antigravity/Gemini CLI is installed in your PATH.")
            sys.exit(1)

    print(f"Selected Agent:    {agent_bin.upper()}")
    print(f"Max Turns:         {args.max_turns}")
    print("="*60 + "\n")

    turn = 0
    while turn < args.max_turns:
        turn += 1
        is_complete, completed_count, pending_count, pending_tasks = parse_progress(progress_file)

        print(f"\n>>> [Round {turn}/{args.max_turns}] Progress: {completed_count} completed, {pending_count} pending")

        if is_complete:
            print("\n🎉 ALL TASKS IN AUTOPILOT_PROGRESS.MD ARE COMPLETED! 🎉")
            print("Finished successfully. Exiting overnight daemon.")
            break

        if pending_count > 0:
            print(f"Next active task: {pending_tasks[0]}")

        # Execute turn
        try:
            return_code = run_agent_turn(agent_bin, args.prompt, project_dir, log_file)
            print(f"Turn {turn} ended with return code {return_code}.")
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user (Ctrl+C). Progress is safely preserved in AUTOPILOT_PROGRESS.md and git.")
            sys.exit(0)
        except Exception as e:
            print(f"⚠️ Warning: Turn failed with exception: {e}")

        # Post-turn check
        is_complete, completed_count, pending_count, _ = parse_progress(progress_file)
        if is_complete:
            print("\n🎉 ALL TASKS COMPLETED AFTER TURN! 🎉")
            break

        print(f"Cooling down for {args.cooldown}s before next turn...")
        time.sleep(args.cooldown)

    if turn >= args.max_turns and not is_complete:
        print(f"\n⚠️ Reached maximum limit of {args.max_turns} turns.")
        print(f"Remaining tasks: {pending_count}. Inspect {progress_file} or {log_file} to review.")

if __name__ == "__main__":
    main()
