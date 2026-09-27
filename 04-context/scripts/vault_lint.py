#!/usr/bin/env python3
"""Health-check the LLM wiki in vault/ (see vault/CLAUDE.md).

Errors (exit 1):
  - a page under vault/wiki/ without YAML frontmatter, or missing one of: title, type, created, updated,
    sources, tags; a title that differs from the file name; a type that does not match its folder
  - a `sources` entry that does not exist in the repository
  - a [[wikilink]] (in any vault file) whose target title has no page
  - an orphan: a wiki page with no inbound [[link]] from another wiki page (index.md and log.md do not count)
  - a wiki page not listed in vault/index.md
  - a `path:line` or `path:start-end` code reference (in backticks) whose file is missing or shorter
    than the line cited, or whose first cited line is blank (the usual sign of drift after an edit)
  - vault/index.md without a "## Current state" section, or one longer than 30 lines

Warnings (printed, exit 0): none yet; add checks here as the wiki grows.

Why a linter: a wiki the model maintains will drift from the code unless something fails when it does. These
checks are mechanical on purpose; drift in meaning (a cited line that now says something else) still needs
a lint pass by a session, as vault/CLAUDE.md describes.

Adapt: FOLDER_TYPES maps each folder under vault/wiki/ to the `type` its pages must declare. Add a row when
you add a folder (and list the folder in vault/CLAUDE.md). CURRENT_STATE_MAX keeps the part of index.md that
the SessionStart hook prints into every session small.

Standard library only. Paths in pages are relative to the repository root.
Example: python3 scripts/vault_lint.py            (from the repo root)
         python3 scripts/vault_lint.py --vault path/to/vault --repo path/to/repo
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REQUIRED = ("title", "type", "created", "updated", "sources", "tags")
FOLDER_TYPES = {
    "components": "component",
    "contracts": "contract",
    "decisions": "decision",
    "concepts": "concept",
    "playbooks": "playbook",
    # add your own, e.g. "endpoints": "endpoint"
}
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
CODE_REF = re.compile(
    r"`([A-Za-z0-9_.][A-Za-z0-9_./ -]*?\.[A-Za-z0-9]+):(\d+)(?:-(\d+))?`"
)
INLINE_CODE = re.compile(r"`[^`\n]*`")
CURRENT_STATE_MAX = 30


def parse_frontmatter(text: str) -> dict | None:
    """Minimal YAML subset: `key: value` and `key: [a, b]` lines between two `---` lines."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    meta = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            return None
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            meta[key.strip()] = [
                v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()
            ]
        else:
            meta[key.strip()] = value.strip("\"'")
    return meta


def line_count(path: Path) -> int:
    with path.open(encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


def check_code_refs(text: str, repo: Path, where: str, errors: list[str]) -> int:
    count = 0
    for m in CODE_REF.finditer(text):
        rel, start, end = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
        count += 1
        target = repo / rel
        if not target.is_file():
            errors.append(f"{where}: `{rel}:{m.group(2)}` file does not exist")
        elif max(start, end) > line_count(target) or start < 1 or end < start:
            errors.append(
                f"{where}: `{m.group(0)[1:-1]}` past end of file ({line_count(target)} lines)"
            )
        elif not first_line(target, start).strip():
            # A citation that starts on a blank line has almost always drifted after an edit.
            errors.append(
                f"{where}: `{m.group(0)[1:-1]}` starts on a blank line (drifted?)"
            )
    return count


def first_line(path: Path, n: int) -> str:
    with path.open(encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            if i == n:
                return line
    return ""


def main() -> int:
    p = argparse.ArgumentParser(
        description="Lint the vault/ wiki: frontmatter, links, orphans, index coverage, code references.",
        epilog="Example: python3 scripts/vault_lint.py   (or --vault other/vault --repo .)",
    )
    p.add_argument("--vault", default="vault", help="vault directory (default: vault)")
    p.add_argument(
        "--repo",
        default=".",
        help="repository root that code references are relative to (default: .)",
    )
    args = p.parse_args()

    repo, vault = Path(args.repo).resolve(), Path(args.vault).resolve()
    wiki = vault / "wiki"
    if not wiki.is_dir():
        print(f"error: {wiki} not found", file=sys.stderr)
        return 2
    errors: list[str] = []
    pages: dict[str, Path] = {}
    per_folder: Counter = Counter()
    for page in sorted(wiki.rglob("*.md")):
        rel = page.relative_to(vault)
        folder = page.relative_to(wiki).parts[0]
        per_folder[folder] += 1
        meta = parse_frontmatter(page.read_text(encoding="utf-8"))
        if meta is None:
            errors.append(f"{rel}: no YAML frontmatter")
            continue
        missing = [k for k in REQUIRED if not meta.get(k)]
        if missing:
            errors.append(f"{rel}: frontmatter missing {missing}")
        if meta.get("title") and meta["title"] != page.stem:
            errors.append(f"{rel}: title {meta['title']!r} differs from file name")
        if FOLDER_TYPES.get(folder) and meta.get("type") != FOLDER_TYPES[folder]:
            errors.append(
                f"{rel}: type {meta.get('type')!r} should be {FOLDER_TYPES[folder]!r}"
            )
        if folder not in FOLDER_TYPES:
            errors.append(
                f"{rel}: folder {folder!r} is not one of {sorted(FOLDER_TYPES)}"
            )
        for src in meta.get("sources") or []:
            path = src.split(":")[0]
            if not (repo / path).exists():
                errors.append(f"{rel}: source {src!r} does not exist")
        if page.stem in pages:
            errors.append(
                f"{rel}: duplicate title (also {pages[page.stem].relative_to(vault)})"
            )
        pages[page.stem] = page

    inbound: dict[str, set[str]] = defaultdict(set)
    code_refs = 0
    for file in sorted(vault.rglob("*.md")):
        text = file.read_text(encoding="utf-8")
        rel = str(file.relative_to(vault))
        for m in WIKILINK.finditer(
            INLINE_CODE.sub("", text)
        ):  # links inside `code` are examples
            target = m.group(1).strip()
            if target not in pages:
                errors.append(f"{rel}: broken link [[{target}]]")
            elif file.parent != vault and target != file.stem:
                inbound[target].add(file.stem)
        code_refs += check_code_refs(text, repo, rel, errors)

    for title, page in pages.items():
        if not inbound[title]:
            errors.append(
                f"{page.relative_to(vault)}: orphan (no inbound link from another wiki page)"
            )

    index = vault / "index.md"
    if not index.is_file():
        errors.append("index.md missing")
    else:
        text = index.read_text(encoding="utf-8")
        listed = {
            m.group(1).strip() for m in WIKILINK.finditer(INLINE_CODE.sub("", text))
        }
        for title, page in pages.items():
            if title not in listed:
                errors.append(f"index.md does not list {page.relative_to(vault)}")
        m = re.search(r"^## Current state\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        if not m:
            errors.append("index.md has no '## Current state' section")
        elif len(m.group(1).strip().splitlines()) > CURRENT_STATE_MAX:
            errors.append(
                f"index.md 'Current state' is longer than {CURRENT_STATE_MAX} lines"
            )
    if not (vault / "log.md").is_file():
        errors.append("log.md missing")

    print(f"vault_lint: {len(pages)} pages, {code_refs} code references checked")
    for folder in sorted(per_folder):
        print(f"  {folder:12} {per_folder[folder]}")
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    print("OK" if not errors else f"{len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
