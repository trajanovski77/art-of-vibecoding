#!/usr/bin/env python3
"""SessionStart hook: orient a new session without being asked.

Prints three things, each small on purpose:
  1. the "## Current state" section of vault/index.md, only that section, so every session starts from the
     wiki's map at a small context cost (the rest of the wiki is read on demand; see 04-context);
  2. the last 15 lines of docs/progress.md, the step log written by /step-done;
  3. `git log --oneline -5`.

For SessionStart, Claude Code adds plain stdout to the session as context (capped at 10,000 characters; over
that, Claude only gets a file path and a preview, so keep the three sections short). It fires on startup,
resume, /clear and compaction, which is exactly when a session has lost its memory.

Reads the hook JSON from stdin and uses only `cwd`. The repository root is the git top level of `cwd`, so a
session working in a git worktree sees that worktree's log, not the main checkout's. Missing files are
reported, not fatal. Always exits 0: a broken orientation hook must never stop a session from starting.
Standard library only.
"""

import json
import os
import re
import subprocess
import sys

PROGRESS_LINES = 15  # /step-done keeps each entry to 12 lines, so the newest entry always fits
LOG_ENTRIES = 5
STATE_MAX_LINES = 40  # vault_lint.py keeps the section at 30; this cap only guards a runaway file


def project_root() -> str:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        payload = {}
    start = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    try:
        result = subprocess.run(
            ["git", "-C", start, "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return os.environ.get("CLAUDE_PROJECT_DIR") or start


def progress_tail(root: str) -> str:
    try:
        with open(
            os.path.join(root, "docs", "progress.md"), encoding="utf-8", errors="replace"
        ) as f:
            return "".join(f.readlines()[-PROGRESS_LINES:]).rstrip()
    except OSError:
        return "(docs/progress.md not found)"


def current_state(root: str) -> str:
    """The body of the '## Current state' section of vault/index.md, up to the next '## ' heading."""
    try:
        with open(
            os.path.join(root, "vault", "index.md"), encoding="utf-8", errors="replace"
        ) as f:
            text = f.read()
    except OSError:
        return "(no vault/index.md: this repo has no wiki yet)"
    match = re.search(r"^## Current state[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not match:
        return "(vault/index.md has no '## Current state' section)"
    return "\n".join(match.group(1).strip().splitlines()[:STATE_MAX_LINES])


def git_log(root: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", root, "log", "--oneline", f"-{LOG_ENTRIES}"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return "(git not available)"
    out = result.stdout.strip()
    return out if result.returncode == 0 and out else "(no commits yet)"


def main() -> int:
    root = project_root()
    print("Session orientation (printed by .claude/hooks/session_start.py)")
    print(
        "\n== vault/index.md: Current state (read vault/index.md for the rest) ==\n"
        f"{current_state(root)}"
    )
    print(f"\n== docs/progress.md (last {PROGRESS_LINES} lines) ==\n{progress_tail(root)}")
    print(f"\n== git log --oneline -{LOG_ENTRIES} ==\n{git_log(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
