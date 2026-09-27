#!/usr/bin/env python3
"""PostToolUse hook (matcher: Edit|Write): format the edited file if a formatter for its language is installed.

Reads the hook JSON from stdin (tool_input.file_path). Does nothing when the file has no known formatter, no
formatter is installed, the file is outside the project, or the formatter fails. Always exits 0: the edit has
already happened, so a PostToolUse hook cannot undo it (exit 2 would only show stderr to Claude), and any
other non-zero code only adds a hook-error notice to the transcript. There is nothing to gain by failing.

Why a hook and not an instruction: "format your code" in CLAUDE.md is a request the model may forget; a hook
runs every time. Formatting after each edit also keeps diffs small, so reviews see only real changes.

Adapt: FORMATTERS maps a file extension to candidate commands; the first installed one wins. Add a row when
your stack adds a language. Standard library only.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

PRETTIER = [["prettier", "--write"]]
FORMATTERS = {
    ".py": [["ruff", "format"], ["black", "-q"]],
    ".go": [["gofmt", "-w"]],
    ".rs": [["rustfmt"]],
    ".sh": [["shfmt", "-w"]],
    ".js": PRETTIER,
    ".jsx": PRETTIER,
    ".ts": PRETTIER,
    ".tsx": PRETTIER,
    ".mjs": PRETTIER,
    ".cjs": PRETTIER,
    ".css": PRETTIER,
    ".yaml": PRETTIER,
    ".yml": PRETTIER,
    ".json": PRETTIER,
}


def find_executable(name: str, root: str) -> str | None:
    """A formatter on PATH, or a project-local one (node_modules/.bin)."""
    return shutil.which(name) or shutil.which(
        name, path=os.path.join(root, "node_modules", ".bin")
    )


def edited_path(payload: dict) -> str | None:
    tool_input = payload.get("tool_input") or {}
    tool_response = payload.get("tool_response")
    response = tool_response if isinstance(tool_response, dict) else {}
    return tool_input.get("file_path") or response.get("filePath")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    root = os.path.realpath(
        os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    )
    path = edited_path(payload)
    if not path:
        return 0
    path = os.path.realpath(path if os.path.isabs(path) else os.path.join(root, path))
    if not os.path.isfile(path) or not path.startswith(root + os.sep):
        return 0
    for command in FORMATTERS.get(os.path.splitext(path)[1].lower(), []):
        exe = find_executable(command[0], root)
        if exe:
            try:
                subprocess.run(
                    [exe, *command[1:], path], cwd=root, capture_output=True, timeout=30
                )
            except (OSError, subprocess.SubprocessError) as error:
                # stderr of a hook that exits 0 goes to the debug log only (claude --debug)
                print(f"format_edited: {command[0]} failed on {path}: {error}", file=sys.stderr)
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
